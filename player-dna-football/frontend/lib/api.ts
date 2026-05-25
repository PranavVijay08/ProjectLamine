import { attributeLabels, numericFeatures, radarFeatures } from "./player-metrics";
import type { ComparisonResponse, Player, SimilarFilters, SimilarPlayer } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

let mockPlayersCache: Player[] | null = null;

export async function getPlayers(query?: string): Promise<Player[]> {
  try {
    return await apiFetch<Player[]>(query ? `/players?q=${encodeURIComponent(query)}` : "/players");
  } catch {
    const players = await loadMockPlayers();
    if (!query) return players.sort(byName);
    const search = query.toLowerCase();
    return players
      .filter((player) => [player.player_name, player.club, player.league].some((value) => value.toLowerCase().includes(search)))
      .sort(byName);
  }
}

export async function getPlayer(playerId: number): Promise<Player | null> {
  try {
    return await apiFetch<Player>(`/players/${playerId}`);
  } catch {
    const players = await loadMockPlayers();
    return players.find((player) => player.player_id === playerId) ?? null;
  }
}

export async function getSimilarPlayers(playerId: number, filters: SimilarFilters = {}): Promise<SimilarPlayer[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const suffix = params.toString() ? `?${params.toString()}` : "";
  try {
    return await apiFetch<SimilarPlayer[]>(`/players/${playerId}/similar${suffix}`);
  } catch {
    const players = await loadMockPlayers();
    return computeSimilarPlayers(players, playerId, filters);
  }
}

export async function comparePlayers(playerId: number, otherPlayerId: number): Promise<ComparisonResponse | null> {
  try {
    return await apiFetch<ComparisonResponse>(`/players/${playerId}/compare/${otherPlayerId}`);
  } catch {
    const players = await loadMockPlayers();
    const player = players.find((item) => item.player_id === playerId);
    const other = players.find((item) => item.player_id === otherPlayerId);
    if (!player || !other) return null;
    return buildComparison(players, player, other);
  }
}

async function loadMockPlayers(): Promise<Player[]> {
  if (mockPlayersCache) return mockPlayersCache;
  const response = await fetch("/players_mock.csv", { cache: "force-cache" });
  const csv = await response.text();
  mockPlayersCache = parseCsv(csv).map(rowToPlayer);
  return mockPlayersCache;
}

function parseCsv(csv: string) {
  const [headerLine, ...lines] = csv.trim().split(/\r?\n/);
  const headers = splitCsvLine(headerLine);
  return lines.map((line) => {
    const values = splitCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index]]));
  });
}

function splitCsvLine(line: string) {
  const values: string[] = [];
  let current = "";
  let inQuotes = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"' && line[index + 1] === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}

function rowToPlayer(row: Record<string, string>): Player {
  const numericKeys = ["player_id", "age", "minutes", ...numericFeatures];
  const parsed = { ...row } as unknown as Player;
  numericKeys.forEach((key) => {
    (parsed as unknown as Record<string, number>)[key] = Number(row[key]);
  });
  return parsed;
}

function computeSimilarPlayers(players: Player[], playerId: number, filters: SimilarFilters): SimilarPlayer[] {
  const selected = players.find((player) => player.player_id === playerId);
  if (!selected) return [];
  const scaled = scalePlayers(players);
  const selectedIndex = players.findIndex((player) => player.player_id === playerId);
  return players
    .map((player, index) => {
      const matching = closestAttributes(scaled[selectedIndex], scaled[index]);
      return {
        player,
        similarity_score: Math.round(similarityPercent(scaled[selectedIndex], scaled[index]) * 10) / 10,
        matching_attributes: matching.map((feature) => attributeLabels[feature]),
        explanation: `${player.player_name} is close to ${selected.player_name} in ${matching.map((feature) => attributeLabels[feature].toLowerCase()).join(", ")}. ${
          player.style_label === selected.style_label
            ? `Both profile as ${selected.style_label.toLowerCase()} players.`
            : `The style labels differ (${selected.style_label} vs ${player.style_label}), but the statistical shape is close.`
        }`
      };
    })
    .filter((item) => item.player.player_id !== playerId)
    .filter((item) => !filters.max_age || item.player.age <= Number(filters.max_age))
    .filter((item) => !filters.league || item.player.league.toLowerCase() === filters.league.toLowerCase())
    .filter((item) => !filters.position || item.player.position.toLowerCase() === filters.position.toLowerCase())
    .filter((item) => !filters.nationality || item.player.nationality.toLowerCase() === filters.nationality.toLowerCase())
    .sort((a, b) => b.similarity_score - a.similarity_score)
    .slice(0, 10);
}

function buildComparison(players: Player[], player: Player, other: Player): ComparisonResponse {
  const scaled = scalePlayers(players);
  const playerIndex = players.findIndex((item) => item.player_id === player.player_id);
  const otherIndex = players.findIndex((item) => item.player_id === other.player_id);
  return {
    player,
    other_player: other,
    similarity_score: Math.round(similarityPercent(scaled[playerIndex], scaled[otherIndex]) * 10) / 10,
    radar_attributes: radarFeatures.map((feature) => ({
      attribute: attributeLabels[feature],
      player: Number(player[feature]),
      other_player: Number(other[feature])
    })),
    attribute_deltas: numericFeatures.map((feature) => ({
      attribute: attributeLabels[feature],
      player_value: Number(player[feature]),
      other_value: Number(other[feature]),
      delta: Number((Number(player[feature]) - Number(other[feature])).toFixed(2))
    }))
  };
}

function scalePlayers(players: Player[]) {
  const means = numericFeatures.map((feature) => average(players.map((player) => Number(player[feature]))));
  const stds = numericFeatures.map((feature, index) => standardDeviation(players.map((player) => Number(player[feature])), means[index]));
  return players.map((player) => numericFeatures.map((feature, index) => (Number(player[feature]) - means[index]) / (stds[index] || 1)));
}

function closestAttributes(selected: number[], other: number[]) {
  return numericFeatures
    .map((feature, index) => ({ feature, delta: Math.abs(selected[index] - other[index]) }))
    .sort((a, b) => a.delta - b.delta)
    .slice(0, 3)
    .map((item) => item.feature);
}

function similarityPercent(a: number[], b: number[]) {
  const dot = a.reduce((sum, value, index) => sum + value * b[index], 0);
  const normA = Math.sqrt(a.reduce((sum, value) => sum + value * value, 0));
  const normB = Math.sqrt(b.reduce((sum, value) => sum + value * value, 0));
  const cosine = dot / (normA * normB || 1);
  return Math.max(0, Math.min(100, ((cosine + 1) / 2) * 100));
}

function average(values: number[]) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function standardDeviation(values: number[], mean: number) {
  return Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length);
}

function byName(a: Player, b: Player) {
  return a.player_name.localeCompare(b.player_name);
}
