package com.example.ecommerce.service

import com.example.ecommerce.model.*
import com.example.ecommerce.repository.AdminNotificationRepository
import com.example.ecommerce.repository.CampaignRecipientRepository
import com.example.ecommerce.repository.PromotionalCampaignRepository
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class CampaignEmailService(
    private val campaignRepository: PromotionalCampaignRepository,
    private val recipientRepository: CampaignRecipientRepository,
    private val adminNotificationRepository: AdminNotificationRepository,
    private val emailGatewayService: EmailGatewayService
) {

    private val logger = LoggerFactory.getLogger(CampaignEmailService::class.java)

    fun processCampaign(campaignId: Long) {
        logger.info("Starting campaign processing for campaign ID: $campaignId")

        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        val pendingRecipients = recipientRepository
            .findByCampaignIdAndStatus(campaignId, RecipientStatus.PENDING)

        logger.info("Found ${pendingRecipients.size} pending recipients for campaign $campaignId")

        pendingRecipients.forEach { recipient ->
            sendCampaignEmail(campaign, recipient)
        }

        updateCampaignStatus(campaign)
    }

    @Async
    fun sendCampaignEmail(campaign: PromotionalCampaign, recipient: CampaignRecipient) {
        logger.debug("Sending campaign email to ${recipient.customerEmail}")

        try {
            emailGatewayService.sendPromotionalEmail(
                to = recipient.customerEmail,
                subject = campaign.subjectLine,
                content = personalizeContent(campaign.emailContent, recipient)
            )

            recipient.status = RecipientStatus.SENT
            recipient.sentAt = LocalDateTime.now()
            recipientRepository.save(recipient)

            logger.info("Successfully sent campaign email to ${recipient.customerEmail}")

        } catch (e: Exception) {
            logger.error("Failed to send email to ${recipient.customerEmail}: ${e.message}")

            recipient.status = RecipientStatus.FAILED
            recipient.errorMessage = e.message
            recipientRepository.save(recipient)
        }
    }

    private fun personalizeContent(content: String, recipient: CampaignRecipient): String {
        return content.replace("{{name}}", recipient.customerName ?: "Valued Customer")
    }

    private fun updateCampaignStatus(campaign: PromotionalCampaign) {
        val allRecipients = recipientRepository
            .findByCampaignIdAndStatus(campaign.id, RecipientStatus.PENDING)

        if (allRecipients.isEmpty()) {
            campaign.status = CampaignStatus.COMPLETED
            campaignRepository.save(campaign)
            logger.info("Campaign ${campaign.id} marked as completed")
        }
    }

    fun retryCampaignFailures(campaignId: Long) {
        logger.info("Retrying failed emails for campaign $campaignId")

        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        val failedRecipients = recipientRepository
            .findByCampaignIdAndStatus(campaignId, RecipientStatus.FAILED)

        logger.info("Retrying ${failedRecipients.size} failed recipients")

        failedRecipients.forEach { recipient ->
            recipient.status = RecipientStatus.PENDING
            recipient.errorMessage = null
            recipientRepository.save(recipient)

            sendCampaignEmail(campaign, recipient)
        }
    }
}
