package com.metatroop.situationalawareness.display

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class DemoDisplayGateway(
    initialCapability: HudCapability = HudCapability.UNAVAILABLE,
) : DisplayGateway {
    private val mutableStatus =
        MutableStateFlow(
            HudStatus(
                capability = initialCapability,
                enabled = initialCapability == HudCapability.READY,
            )
        )

    override val status: StateFlow<HudStatus> = mutableStatus.asStateFlow()

    override suspend fun prepare() {
        if (mutableStatus.value.capability != HudCapability.UNAVAILABLE) {
            mutableStatus.value = mutableStatus.value.copy(capability = HudCapability.READY)
        }
    }

    override suspend fun setEnabled(enabled: Boolean) {
        val canEnable = mutableStatus.value.capability == HudCapability.READY
        mutableStatus.value = mutableStatus.value.copy(enabled = enabled && canEnable)
    }

    override suspend fun show(card: HudCard) {
        val current = mutableStatus.value
        if (current.capability == HudCapability.READY && current.enabled) {
            mutableStatus.value = current.copy(lastCard = card)
        }
    }

    override suspend fun clear() {
        mutableStatus.value = mutableStatus.value.copy(lastCard = null)
    }
}
