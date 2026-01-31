package com.example.ecommerce.service

import com.example.ecommerce.model.*
import com.example.ecommerce.repository.*
import kotlinx.coroutines.delay
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class MarketingCampaignService(
    private val campaignRepository: MarketingCampaignRepository,
    private val subscriberRepository: CampaignSubscriberRepository,
    private val campaignSendRepository: CampaignSendRepository,
    private val emailRateLimitRepository: EmailRateLimitRepository,
    private val bulkEmailService: BulkEmailService
) {

    private val logger = LoggerFactory.getLogger(MarketingCampaignService::class.java)

    fun executeCampaign(campaignId: Long) {
        logger.info("Starting campaign execution for campaign ID: $campaignId")

        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        require(campaign.status == CampaignStatus.SCHEDULED || campaign.status == CampaignStatus.DRAFT) {
            "Campaign must be in SCHEDULED or DRAFT status to execute"
        }

        val activeSubscribers = subscriberRepository.findByIsActiveTrue()

        if (activeSubscribers.isEmpty()) {
            logger.warn("No active subscribers found for campaign $campaignId")
            campaign.status = CampaignStatus.COMPLETED
            campaignRepository.save(campaign)
            return
        }

        campaign.status = CampaignStatus.RUNNING
        campaign.startedAt = LocalDateTime.now()
        campaign.totalRecipients = activeSubscribers.size
        campaignRepository.save(campaign)

        logger.info("Campaign $campaignId: sending to ${activeSubscribers.size} subscribers")

        val campaignSends = activeSubscribers.map { subscriber ->
            CampaignSend(
                campaignId = campaign.id,
                subscriberId = subscriber.id,
                status = SendStatus.PENDING
            )
        }
        campaignSendRepository.saveAll(campaignSends)

        sendCampaignEmails(campaign, activeSubscribers)

        campaign.status = CampaignStatus.COMPLETED
        campaign.completedAt = LocalDateTime.now()
        campaignRepository.save(campaign)

        logger.info("Campaign $campaignId completed. Sent: ${campaign.sentCount}, Failed: ${campaign.failedCount}")
    }

    private fun sendCampaignEmails(campaign: MarketingCampaign, subscribers: List<CampaignSubscriber>) {
        var successCount = 0
        var failureCount = 0

        subscribers.forEach { subscriber ->
            try {
                bulkEmailService.sendMarketingEmail(
                    to = subscriber.email,
                    subject = campaign.subject,
                    body = personalizeEmailBody(campaign.emailBody, subscriber)
                )

                updateSendStatus(campaign.id, subscriber.id, SendStatus.SENT, null)
                successCount++

                logger.debug("Email sent to ${subscriber.email} for campaign ${campaign.id}")

            } catch (e: Exception) {
                logger.error("Failed to send email to ${subscriber.email}: ${e.message}", e)

                updateSendStatus(campaign.id, subscriber.id, SendStatus.FAILED, e.message)
                failureCount++
            }
        }

        campaign.sentCount = successCount
        campaign.failedCount = failureCount
        campaignRepository.save(campaign)
    }

    private fun personalizeEmailBody(body: String, subscriber: CampaignSubscriber): String {
        return body
            .replace("{{name}}", subscriber.fullName ?: "Valued Customer")
            .replace("{{email}}", subscriber.email)
    }

    private fun updateSendStatus(campaignId: Long, subscriberId: Long, status: SendStatus, errorMessage: String?) {
        val campaignSends = campaignSendRepository.findByCampaignIdAndStatus(campaignId, SendStatus.PENDING)
        val send = campaignSends.firstOrNull { it.subscriberId == subscriberId }

        if (send != null) {
            send.status = status
            send.sentAt = LocalDateTime.now()
            send.errorMessage = errorMessage
            campaignSendRepository.save(send)
        }
    }

    fun getCampaignProgress(campaignId: Long): CampaignProgress {
        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        val pendingCount = campaignSendRepository
            .findByCampaignIdAndStatus(campaignId, SendStatus.PENDING).size

        return CampaignProgress(
            campaignId = campaign.id,
            campaignName = campaign.name,
            status = campaign.status,
            totalRecipients = campaign.totalRecipients,
            sentCount = campaign.sentCount,
            failedCount = campaign.failedCount,
            pendingCount = pendingCount,
            startedAt = campaign.startedAt,
            completedAt = campaign.completedAt
        )
    }

    fun pauseCampaign(campaignId: Long) {
        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        require(campaign.status == CampaignStatus.RUNNING) {
            "Only running campaigns can be paused"
        }

        campaign.status = CampaignStatus.PAUSED
        campaignRepository.save(campaign)

        logger.info("Campaign $campaignId paused")
    }

    fun resumeCampaign(campaignId: Long) {
        val campaign = campaignRepository.findById(campaignId)
            .orElseThrow { IllegalArgumentException("Campaign not found: $campaignId") }

        require(campaign.status == CampaignStatus.PAUSED) {
            "Only paused campaigns can be resumed"
        }

        campaign.status = CampaignStatus.RUNNING
        campaignRepository.save(campaign)

        val pendingSends = campaignSendRepository.findByCampaignIdAndStatus(campaignId, SendStatus.PENDING)
        val pendingSubscribers = pendingSends.mapNotNull { send ->
            subscriberRepository.findById(send.subscriberId).orElse(null)
        }

        sendCampaignEmails(campaign, pendingSubscribers)

        campaign.status = CampaignStatus.COMPLETED
        campaign.completedAt = LocalDateTime.now()
        campaignRepository.save(campaign)

        logger.info("Campaign $campaignId resumed and completed")
    }
}

data class CampaignProgress(
    val campaignId: Long,
    val campaignName: String,
    val status: CampaignStatus,
    val totalRecipients: Int,
    val sentCount: Int,
    val failedCount: Int,
    val pendingCount: Int,
    val startedAt: LocalDateTime?,
    val completedAt: LocalDateTime?
)
