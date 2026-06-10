package com.metatroop.situationalawareness.display

import com.metatroop.situationalawareness.alert.Alert

class AlertHudMapper {
    fun toHudCard(alert: Alert): HudCard {
        return HudCard(
            title = alert.message.substringBefore(",").replaceFirstChar { it.uppercase() },
            detail = "Visible hazard observation",
            confidencePercent = (alert.confidence * 100).toInt(),
            severity = alert.severity,
        )
    }
}
