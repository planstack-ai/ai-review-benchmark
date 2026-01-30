package com.example.campaign.service;

import com.example.campaign.entity.Campaign;
import com.example.campaign.repository.CampaignRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class CampaignService {

    private final CampaignRepository campaignRepository;
    private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Autowired
    public CampaignService(CampaignRepository campaignRepository) {
        this.campaignRepository = campaignRepository;
    }

    public boolean isCampaignActive(Long campaignId) {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId);
        if (campaignOpt.isEmpty()) {
            return false;
        }

        Campaign campaign = campaignOpt.get();
        return isWithinActivePeriod(campaign) && hasValidBudget(campaign);
    }

    public List<Campaign> getActiveCampaigns() {
        List<Campaign> allCampaigns = campaignRepository.findAll();
        return allCampaigns.stream()
                .filter(this::isWithinActivePeriod)
                .filter(this::hasValidBudget)
                .toList();
    }

    public BigDecimal calculateRemainingBudget(Long campaignId) {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId);
        if (campaignOpt.isEmpty()) {
            return BigDecimal.ZERO;
        }

        Campaign campaign = campaignOpt.get();
        BigDecimal totalBudget = campaign.getTotalBudget();
        BigDecimal spentAmount = campaign.getSpentAmount();
        
        return totalBudget.subtract(spentAmount);
    }

    private boolean isWithinActivePeriod(Campaign campaign) {
        LocalDateTime currentTime = LocalDateTime.now();
        LocalDateTime startTime = campaign.getStartDateTime();
        LocalDateTime endTime = campaign.getEndDateTime();

        return currentTime.isAfter(startTime) && currentTime.isBefore(endTime);
    }

    private boolean hasValidBudget(Campaign campaign) {
        BigDecimal remainingBudget = calculateRemainingBudget(campaign.getId());
        return remainingBudget.compareTo(BigDecimal.ZERO) > 0;
    }

    public void updateCampaignStatus(Long campaignId) {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId);
        if (campaignOpt.isEmpty()) {
            return;
        }

        Campaign campaign = campaignOpt.get();
        boolean isActive = isCampaignActive(campaignId);
        
        if (isActive && !campaign.isActive()) {
            campaign.setActive(true);
            campaign.setLastUpdated(LocalDateTime.now());
            campaignRepository.save(campaign);
        } else if (!isActive && campaign.isActive()) {
            campaign.setActive(false);
            campaign.setLastUpdated(LocalDateTime.now());
            campaignRepository.save(campaign);
        }
    }

    public String getCampaignStatusReport(Long campaignId) {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId);
        if (campaignOpt.isEmpty()) {
            return "Campaign not found";
        }

        Campaign campaign = campaignOpt.get();
        LocalDateTime currentTime = LocalDateTime.now();
        boolean isActive = isCampaignActive(campaignId);
        BigDecimal remainingBudget = calculateRemainingBudget(campaignId);

        return String.format("Campaign %s - Status: %s, Current Time: %s, Remaining Budget: %s",
                campaign.getName(),
                isActive ? "ACTIVE" : "INACTIVE",
                currentTime.format(formatter),
                remainingBudget.toString());
    }
}