<!-- badges: start -->
[![Licence: CERN-OHL-S v2](https://img.shields.io/badge/hardware-CERN--OHL--S%20v2-873671)](LICENSE-CERN-OHL-S-2.0.md)
[![Licence: CC BY 4.0](https://img.shields.io/badge/docs%20%26%20data-CC%20BY%204.0-457ec1)](LICENSE-CC-BY-4.0.md)
[![DOI](https://img.shields.io/badge/DOI-pending%20first%20release-lightgrey)](CITATION.cff)
[![Deploy site to GitHub Pages](https://github.com/Global-Health-Engineering/3dplam/actions/workflows/deploy-site.yml/badge.svg)](https://github.com/Global-Health-Engineering/3dplam/actions/workflows/deploy-site.yml)
<!-- badges: end -->

<br>
<p align="middle">
<img src="site/public/brand/ETH_GHE_logo.svg" width="480" alt="Global Health Engineering, ETH Zurich">
</p>

# 3DPLAM

- **Moreno Gabriel** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0009-0008-8260-2625](https://orcid.org/0009-0008-8260-2625) (ETH Zürich, Global Health Engineering) *design, construction, testing, writing*
- **Jakub Tkaczuk** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0000-0001-7997-9423](https://orcid.org/0000-0001-7997-9423) (ETH Zürich, Global Health Engineering) *supervision, page development & maintenance*
- **Caetano Dorea** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0000-0001-9367-0668](https://orcid.org/0000-0001-9367-0668) (University of Victoria) *supervision*
- **Elizabeth Tilley** [![ORCID](https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png) 0000-0002-2095-9724](https://orcid.org/0000-0002-2095-9724) (ETH Zürich, Global Health Engineering) *supervision*

**Open-source, 3D-printable membrane-filtration manifold for *Escherichia coli* quantification in drinking water.** Three printed parts (base, funnel and filter support, all printable without support structures on any FDM printer) test drinking water with a syringe and a membrane filter. Validated against a Millipore EZ-Fit™ stainless-steel manifold as the **reference instrument** for the household drinking-water testing used in WHO/UNICEF water-quality surveys. 3DPLAM does not replace the Millipore EZ-Fit™; its contribution is that the design is open and can be printed locally at low cost, whereas the reference instrument can only be bought, at a comparatively high price.

**Full site, with photos, renders and the print-settings requirement are available [here](https://global-health-engineering.github.io/3dplam/).**

## At a glance

| Characteristic       | Description                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------ |
| Parts                | Base + funnel + filter support (2 concurrent alternatives), no supports                    |
| Material cost        | ≈ $0.80 per set (ABS)                                                                      |
| Mass                 | ≈ 32 g                                                                                     |
| Print time           | ≈ 100 min                                                                                  |
| Reference instrument | Millipore EZ-Fit™ stainless-steel manifold (≈ $2,460)                                      |
| Validation           | 8 sites × 3 manifolds × 3 replicates = 72 filtrations, 16 printed-vs-reference comparisons |
| Headline result      | **15 of 16** classifications accepted within the 5 % WHO boundary-tolerance rule; **12 of 16** match exactly with no tolerance applied |
| Sustainable route    | Funnel and filter support printable in rPET from recycled bottles                          |

## Quick start

1. Read [`hardware/README.md`](hardware/README.md) for the parts table, envelopes, and the choice between the two filter-support and two funnel variants.
2. A manifold sliced at default settings is porous: the syringe draws air through the walls instead of pulling water through the membrane, and filtration fails. Import the profile for your printer from [`hardware/print-profiles/`](hardware/print-profiles/) and read [`hardware/print-profiles/README.md`](hardware/print-profiles/README.md) for the any-slicer equivalents.
3. Print `stl/base.stl`, `stl/funnel.stl` and `stl/filter-support-strand-mesh.stl` (the default, validated filter support) as separate jobs.
4. Assemble and operate the manifold following [`docs/assembly.md`](docs/assembly.md) and [`docs/operation.md`](docs/operation.md).

When printing in recycled PET instead of ABS, use the geometry in [`hardware/rpet/`](hardware/rpet/), not `hardware/stl/` and see [`docs/rpet.md`](docs/rpet.md).

## Repository layout

```
hardware/              CERN-OHL-S v2: the parts to print
├── README.md          Parts table, envelopes, variant choices
├── stl/               Printable meshes (millimetres)
├── step/              Editable B-rep: modify the design here
├── rpet/              Shrinkage-compensated geometry for recycled PET
├── assembly/          Reference assembly (not a printable part)
├── print-profiles/    Slicer settings for a gas-tight print
└── onshape.md         Source CAD in Onshape, copy it and edit your own

docs/                  CC BY 4.0: how to print, build, run and interpret it
├── printing.md        Print settings, orientation, materials matrix
├── assembly.md        Putting the three parts together
├── operation.md       The E. coli filtration protocol
├── validation.md      What was tested and the headline result
├── rpet.md            Bottle-to-filament, with upstream credit
├── design-history.md  Version history predating this repository
└── thesis.pdf         The BSc thesis this release is drawn from

data/                  CC BY 4.0: the tidied functional and material test data
tools/                 Scripts that regenerate every figure and gate CI
site/                  This repository's GitHub Pages site (Astro)
CITATION.cff           Machine-readable citation metadata
```

## Citation

If you use this hardware, please cite it; see [`CITATION.cff`](CITATION.cff) for the machine-readable record:

> 3DPLAM, 3D-Printed Lightweight Affordable Manifold for Microbial Water
> Quality Testing. Moreno Gabriel, Jakub Tkaczuk, Caetano Dorea, Elizabeth Tilley.
> ETH Zürich, Global Health Engineering.
> https://github.com/Global-Health-Engineering/3dplam

## License

Different parts of this repository are released under different licenses, following standard practice for open-hardware projects:

| Component                                                    | License                                    |
| ------------------------------------------------------------ | ------------------------------------------ |
| Hardware design (CAD, STL, STEP in [`hardware/`](hardware/)) | [CERN-OHL-S v2](LICENSE-CERN-OHL-S-2.0.md) |
| Documentation ([`docs/`](docs/), this README)                | [CC BY 4.0](LICENSE-CC-BY-4.0.md)          |
| Datasets ([`data/`](data/))                                  | [CC BY 4.0](LICENSE-CC-BY-4.0.md)          |
| Site and tooling ([`site/`](site/), [`tools/`](tools/))      | [CC BY 4.0](LICENSE-CC-BY-4.0.md)          |

The rPET route in [`hardware/rpet/`](hardware/rpet/) and [`docs/rpet.md`](docs/rpet.md) rebuilds **Petamentor2**, an open-source PET-bottle-to-filament machine designed by **Ondřej Šraitr** (<https://petamentor2.com/>), credited, not redistributed; build your own from the upstream project.
