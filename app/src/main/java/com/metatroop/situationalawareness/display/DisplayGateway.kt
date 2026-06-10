package com.metatroop.situationalawareness.display

import kotlinx.coroutines.flow.StateFlow

interface DisplayGateway {
    val status: StateFlow<HudStatus>

    suspend fun prepare()
    suspend fun setEnabled(enabled: Boolean)
    suspend fun show(card: HudCard)
    suspend fun clear()
}
