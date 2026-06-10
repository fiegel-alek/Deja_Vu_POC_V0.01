package com.metatroop.situationalawareness.alert

data class Detection(
    val label: String,
    val confidence: Double,
    val timestampMs: Long,
    val direction: String? = null,
)

data class DetectionClass(
    val label: String,
    val spokenName: String,
    val threshold: Double,
    val severity: Int,
)

data class AlertPolicy(
    val classesByLabel: Map<String, DetectionClass>,
    val defaultCooldownMs: Long,
    val maxAlertsPerFrame: Int,
)

data class Alert(
    val label: String,
    val confidence: Double,
    val timestampMs: Long,
    val message: String,
    val severity: Int,
)

class AlertEngine(private val policy: AlertPolicy) {
    private val lastAlertByLabel = mutableMapOf<String, Long>()

    fun evaluate(detections: List<Detection>): List<Alert> {
        val candidates = detections.mapNotNull { detection ->
            val detectionClass = policy.classesByLabel[detection.label] ?: return@mapNotNull null
            if (detection.confidence < detectionClass.threshold) return@mapNotNull null

            val lastAlertMs = lastAlertByLabel[detection.label]
            if (lastAlertMs != null && detection.timestampMs - lastAlertMs < policy.defaultCooldownMs) {
                return@mapNotNull null
            }

            detection.toAlert(detectionClass)
        }

        val alerts = candidates
            .sortedWith(compareByDescending<Alert> { it.severity }.thenByDescending { it.confidence })
            .take(policy.maxAlertsPerFrame)

        alerts.forEach { alert -> lastAlertByLabel[alert.label] = alert.timestampMs }
        return alerts
    }

    private fun Detection.toAlert(detectionClass: DetectionClass): Alert {
        val confidencePercent = (confidence * 100).toInt()
        val directionText = direction?.let { " $it" }.orEmpty()
        return Alert(
            label = label,
            confidence = confidence,
            timestampMs = timestampMs,
            message = "${detectionClass.spokenName}$directionText, $confidencePercent percent.",
            severity = detectionClass.severity,
        )
    }
}
