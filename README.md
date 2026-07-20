# aas-digital-twin-Afriso

This project aims to build and manage Asset Administration Shells (AAS) for Afriso industrial products.

### 1. Asset Information
- **asset_kind**: Type (`AssetKind.TYPE`)
- **global_asset_id**: Afriso product details page URL.

### 2. Asset Administration Shell (AAS)
- **id_short**: `LAG14ER`
- **id_**: `https://www.afriso.com/aas/LAG14ER` (Globally unique identifier (URI) that can be used directly as an API endpoint (HTTP GET) on the Afriso AAS registry server.)
- **display_name**: Multi-language name.
- **description**: Product designation in German (`Steuergerät LAG-14 ER / Leckanzeiger`)
- **administration**: AAS metadata versioning initialized at `1.0`.
- **Submodel References**:
  - `Digital Nameplate`
  - `Handover Documentation`
  - `Technical Data`
  - `Carbon Footprint`
  - `Maintenance Instructions`
  