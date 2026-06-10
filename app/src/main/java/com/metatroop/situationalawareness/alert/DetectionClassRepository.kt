package com.metatroop.situationalawareness.alert

import android.content.res.AssetManager
import org.json.JSONObject

class DetectionClassRepository(private val assets: AssetManager) {
    fun load(): AlertPolicy {
        val payload = assets.open("detection_classes.json")
            .bufferedReader()
            .use { reader -> JSONObject(reader.readText()) }

        val classes = payload.getJSONArray("classes")
        val classesByLabel = buildMap {
            for (index in 0 until classes.length()) {
                val item = classes.getJSONObject(index)
                val detectionClass = DetectionClass(
                    label = item.getString("label"),
                    spokenName = item.getString("spoken_name"),
                    threshold = item.getDouble("threshold"),
                    severity = item.getInt("severity"),
                )
                put(detectionClass.label, detectionClass)
            }
        }

        return AlertPolicy(
            classesByLabel = classesByLabel,
            defaultCooldownMs = payload.optLong("default_cooldown_ms", 5_000),
            maxAlertsPerFrame = payload.optInt("max_alerts_per_frame", 1),
        )
    }
}
