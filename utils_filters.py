def sync_select_all(all_selected, input, selected, all_options, triggered_id):
    """
    Helper function. Many inputs have multiple selections and for ease of use, come with a
    'select all' checkbox. This func is passed into circular callbacks to synchronize
    the checkbox with the input selections.

    ----- Arguments -----
    all_selected: Value of checkbox. Either ['Select all'] or []
    input: The dcc input, usually a dcc.Dropdown. Matches the Input in the callback.
    selected: The value of the dcc input, a list.
    all_options: All possible options for the dcc input, obtained from datasets from mod_dataworld
    ctx: The callback_context.

    Returns: all_selected, selected
    """
    if triggered_id == input.id:
        all_selected = ['Select all'] if set(selected) == set(all_options) else []
    else:
        selected = all_options if all_selected else []
    return all_selected, selected
