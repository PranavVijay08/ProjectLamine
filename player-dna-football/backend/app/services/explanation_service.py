ATTRIBUTE_LABELS = {
    "goals_per90": "goal output",
    "assists_per90": "assist output",
    "xg_per90": "shot quality",
    "xa_per90": "chance creation",
    "shots_per90": "shot volume",
    "key_passes_per90": "key passing",
    "progressive_passes_per90": "progressive passing",
    "progressive_carries_per90": "progressive carrying",
    "successful_dribbles_per90": "successful dribbling",
    "pass_completion_pct": "passing security",
    "touches_attacking_third_per90": "attacking-third involvement",
    "pressures_per90": "pressing volume",
    "tackles_per90": "tackling activity",
    "interceptions_per90": "interception activity",
    "aerial_win_pct": "aerial strength",
    "defensive_duels_won_pct": "defensive duel success",
    "carries_into_box_per90": "box carries",
    "passes_into_box_per90": "box entries by pass",
    "final_third_entries_per90": "final-third entries",
}


def readable_attribute(attribute: str) -> str:
    return ATTRIBUTE_LABELS.get(attribute, attribute.replace("_", " "))


def build_similarity_explanation(
    selected_name: str,
    similar_name: str,
    matching_attributes: list[str],
    selected_style: str,
    similar_style: str,
) -> str:
    readable = [readable_attribute(attribute) for attribute in matching_attributes]
    if len(readable) >= 3:
        attribute_text = f"{readable[0]}, {readable[1]} and {readable[2]}"
    else:
        attribute_text = ", ".join(readable)

    style_text = (
        f"Both profile as {selected_style.lower()} players"
        if selected_style == similar_style
        else f"Their style labels differ ({selected_style} vs {similar_style}), but the statistical shape is close"
    )
    return f"{similar_name} is close to {selected_name} in {attribute_text}. {style_text}."
