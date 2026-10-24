# Kestrel Air personas: file format

One file per persona in code/personas/ (any name ending .md; files starting with '_' are ignored).
A file may also hold several personas. The parser checks every file:
- '## <id>' starts a persona. Under it, before any section: '- group:', '- name:', '- narrative:'.
- Then '### <section>' blocks named after the audience attribute catalog (03-audience-attributes.md):
  A. Demographic · B. Life story · C. Values and attitudes · D. Behavior · E. Emotions and reactions ·
  F. Social and information · G. Money pressure · H. What they can do · I. Lifestyle and personal details ·
  J. Kestrel Air (sector) for the dossier's sector attributes.
  Each holds '- field: value' lines; use only the fields that matter, any order.
- Required: group, name, narrative; age and state (A); route (domestic | mexico_caribbean),
  trip_weeks (weeks 1-10 with a booked Kestrel flight, e.g. 4, 8) and reason_for_the_trip (J).
- '### custom': free text for this persona only, added to its prompt as is.
Every persona gets the same templates from prompts.json; its sections fill $profile and its custom text fills $custom.

To switch a persona off without deleting it, wrap its block (or the whole file) in <!-- and -->.
