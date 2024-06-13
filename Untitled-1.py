< manifest
xmlns: android = "http://schemas.android.com/apk/res/android"
package = "com.example.smsforwarder" >

< uses - permission
android: name = "android.permission.RECEIVE_SMS" / >
< uses - permission
android: name = "android.permission.INTERNET" / >
< uses - permission
android: name = "android.permission.ACCESS_NETWORK_STATE" / >

< application
android: allowBackup = "true"
android: icon = "@mipmap/ic_launcher"
android: label = "@string/app_name"
android: roundIcon = "@mipmap/ic_launcher_round"
android: supportsRtl = "true"
android: theme = "@style/AppTheme" >

< receiver
android: name = ".SmsReceiver"
android: exported = "true" >
< intent - filter >
< action
android: name = "android.provider.Telephony.SMS_RECEIVED" / >
< / intent - filter >
< / receiver >
< / application >

< / manifest >
package com.example.smsforwarder

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.telephony.SmsMessage
import android.util.Log
import okhttp3.*

class SmsReceiver : BroadcastReceiver() {
    private val TAG = "SmsReceiver"
    private val BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    private val CHAT_ID = "YOUR_CHAT_ID"

    override fun onReceive(context: Context, intent: Intent) {
        val bundle: Bundle? = intent.extras
        val pdus = bundle?.get("pdus") as Array<*>?
        val messages = pdus?.map { pdu ->
            val format = bundle.getString("format")
            SmsMessage.createFromPdu(pdu as ByteArray, format)
        }

        messages?.forEach { message ->
            val msgBody = message?.messageBody
            val msgSender = message?.originatingAddress
            Log.d(TAG, "SMS from $msgSender: $msgBody")

            val text = "SMS from $msgSender: $msgBody"
            sendMessageToTelegram(text)
        }
    }


    private fun sendMessageToTelegram(text: String) {
        val url = "https://api.telegram.org/bot$BOT_TOKEN/sendMessage"
        val client = OkHttpClient()
        val formBody = FormBody.Builder()
            .add("chat_id", CHAT_ID)
            .add("text", text)
            .build()
        val request = Request.Builder()
            .url(url)
            .post(formBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e(TAG, "Failed to send message: $e")
            }

            override fun onResponse(call: Call, response: Response) {
                if (!response.isSuccessful) {
                    Log.e(TAG, "Failed to send message: ${response.body?.string()}")
                }
            }
        })
    }
}
