# Design records and MCP

Follow [shared MCP operations](../../strato/references/mcp-operations.md) for bulk writes, revision checks, governed changes, and sync history.

Architecture and detailed design are ordinary `design_element` records with Markdown descriptions, not separate record types. Software and Hardware Specifications are `software_specification` and `hardware_specification`; mechanical requirements use Hardware Specifications. Classify requirements by what they constrain and the product's conventions, rather than the source file format or repository label.

Specifications expose `implemented_by_design_elements`. Design Elements own `linked_software_specifications` and `linked_hardware_specifications`. Both links may be supplied on Design Element creation and update. Reread both link categories before replacing either. A diagram embedded in a description does not itself establish a specification relationship. Specification `linked_product_requirements` also uses the shared replacement semantics.

Rich-text reads and writes use Markdown. Preserve fenced Mermaid source. Use `dhf_kicad_upload_v1` only when advertised and enabled. KiCad uploads return immutable artifact identities and insertion Markdown; use those values exactly and preserve tenant/product scope. Artifact references alone do not expose source bytes; use the advertised read/upload tools for each supported format.
