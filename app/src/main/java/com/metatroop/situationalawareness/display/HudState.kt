package com.metatroop.situationalawareness.display

enum class HudCapability {
    UNAVAILABLE,
    PREPARING,
    READY,
    ERROR,
}

data class HudCard(
    val title: String,
    val detail: String,
    val confidencePercent: Int,
    val severity: Int,
)

data class HudStatus(
    val capability: HudCapability = HudCapability.UNAVAILABLE,
    val enabled: Boolean = false,
    val lastCard: HudCard? = null,
) {
    val displayText: String
        get() =
            when (capability) {
                HudCapability.UNAVAILABLE -> "HUD unavailable"
                HudCapability.PREPARING -> "HUD preparing"
                HudCapability.READY -> if (enabled) "HUD ready" else "HUD muted"
                HudCapability.ERROR -> "HUD error"
            }
}
