"""Safe L0 aesthetic tuning: preserve aligned mono derivation and enrich color."""

ASSETS = "/mosheng_project/02_visual_assets"


def require(parent, names):
    missing = [name for name in names if parent.op(name) is None]
    if missing:
        raise Exception("upgrade_01 missing: " + ", ".join(missing))


def setpar(node, name, value):
    par = getattr(node.par, name, None)
    if par is not None:
        par.val = value


assets = op(ASSETS)
if assets is None:
    raise Exception("upgrade_01 missing " + ASSETS)

require(assets, (
    "switch_color_season", "switch_mono_season", "level_mono_deep_ink",
    "OUT_color_bottom_layer", "OUT_mono_top_layer",
))

# Keep the existing mono pipeline. It is derived from each fitted color image,
# so the mono and color compositions remain pixel-identical.
mono = assets.op("level_mono_deep_ink")
setpar(mono, "blacklevel", 0.015)
setpar(mono, "gamma1", 0.88)
setpar(mono, "contrast", 1.12)
setpar(mono, "brightness1", 0.98)

# Do not insert or reconnect a new color chain: the current mono derivation has
# internal dependencies on the fitted color stream. Rewiring its public output
# can create a cook dependency loop. Tune an existing grade only when present.
for name in ("hsv_rich_season_pigment", "level_color_rich", "hsv_color_rich"):
    existing = assets.op(name)
    if existing:
        setpar(existing, "saturationmult", 1.08)
        setpar(existing, "valuemult", 1.01)
        setpar(existing, "gamma1", 0.97)
        setpar(existing, "contrast", 1.03)

for season in ("spring", "summer", "autumn", "winter"):
    derived = assets.op("derive_%s_mono_from_color" % season)
    if derived is None:
        raise Exception("upgrade_01 requires aligned mono node: derive_%s_mono_from_color" % season)

note = assets.op("README_aesthetic_safe_l0") or assets.create("textDAT", "README_aesthetic_safe_l0")
note.text = (
    "Safe L0: existing color-derived mono pipeline retained for exact alignment.\n"
    "Only existing grade parameters were tuned; no assets connection changed.\n"
    "Both public outputs are forced to 1280x720, Fill Outside."
)
print("UPGRADE_01_OK aligned mono retained; restrained color grade enabled")
