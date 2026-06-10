package com.metatroop.situationalawareness

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.metatroop.situationalawareness.alert.AlertEngine
import com.metatroop.situationalawareness.alert.DetectionClassRepository
import com.metatroop.situationalawareness.alert.InMemoryAlertLogRepository
import com.metatroop.situationalawareness.device.DemoGlassesGateway
import com.metatroop.situationalawareness.display.AlertHudMapper
import com.metatroop.situationalawareness.display.DemoDisplayGateway
import com.metatroop.situationalawareness.display.HudCapability
import com.metatroop.situationalawareness.monitoring.FrameProcessor
import com.metatroop.situationalawareness.ui.SituationalAwarenessViewModel
import com.metatroop.situationalawareness.ui.SituationalAwarenessViewModelFactory
import com.metatroop.situationalawareness.vision.DemoHazardDetector
import com.metatroop.situationalawareness.vision.FrameSampler

class MainActivity : ComponentActivity() {
    private val viewModel: SituationalAwarenessViewModel by viewModels {
        val repository = DetectionClassRepository(assets)
        val alertEngine = AlertEngine(repository.load())
        SituationalAwarenessViewModelFactory(
            glassesGateway = DemoGlassesGateway(),
            frameProcessor = FrameProcessor(
                frameSampler = FrameSampler(),
                hazardDetector = DemoHazardDetector(),
                alertEngine = alertEngine,
            ),
            alertLogRepository = InMemoryAlertLogRepository(),
            displayGateway = DemoDisplayGateway(initialCapability = HudCapability.UNAVAILABLE),
            alertHudMapper = AlertHudMapper(),
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AwarenessScreen(viewModel)
                }
            }
        }
    }
}

@Composable
private fun AwarenessScreen(viewModel: SituationalAwarenessViewModel) {
    val state by viewModel.state.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Situational Awareness", style = MaterialTheme.typography.headlineMedium)
        Text(state.sessionState.displayText, style = MaterialTheme.typography.bodyLarge)

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Monitoring")
            Switch(
                checked = state.monitoring,
                onCheckedChange = { enabled ->
                    if (enabled) viewModel.startMonitoring() else viewModel.stopMonitoring()
                },
            )
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(state.hudStatus.displayText)
            Switch(
                checked = state.hudStatus.enabled,
                enabled = state.hudStatus.capability == HudCapability.READY,
                onCheckedChange = viewModel::setHudEnabled,
            )
        }

        Button(
            onClick = { viewModel.simulateHighConfidenceDetection() },
            enabled = state.monitoring,
        ) {
            Text("Simulate detection")
        }

        Spacer(modifier = Modifier.height(8.dp))
        Text("Telemetry", style = MaterialTheme.typography.titleMedium)
        Text("Frames seen: ${state.framesSeen}")
        Text("Frames processed: ${state.framesProcessed}")
        Text("Detections evaluated: ${state.detectionsEvaluated}")
        Text("Alerts spoken: ${state.alertsSpoken}")

        Spacer(modifier = Modifier.height(8.dp))
        Text("Last callout", style = MaterialTheme.typography.titleMedium)
        Text(state.lastAlertMessage.ifBlank { "None" })

        state.hudStatus.lastCard?.let { card ->
            Spacer(modifier = Modifier.height(8.dp))
            Text("HUD preview", style = MaterialTheme.typography.titleMedium)
            Text("${card.title}, ${card.confidencePercent} percent")
        }

        Spacer(modifier = Modifier.height(8.dp))
        Text("Recent alerts", style = MaterialTheme.typography.titleMedium)
        state.alertLog.take(3).forEach { entry ->
            Text(entry.message)
        }
    }
}
