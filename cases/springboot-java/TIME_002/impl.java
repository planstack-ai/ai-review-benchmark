package com.example.campaign.service;

import com.example.campaign.entity.Campaign;
import com.example.campaign.entity.CampaignParticipation;
import com.example.campaign.repository.CampaignRepository;
import com.example.campaign.repository.CampaignParticipationRepository;
import com.example.campaign.exception.CampaignNotFoundException;
import com.example.campaign.exception.CampaignNotActiveException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class CampaignService {

    private final CampaignRepository campaignRepository;
    private final CampaignParticipationRepository participationRepository;

    @Autowired
    public CampaignService(CampaignRepository campaignRepository, 
                          CampaignParticipationRepository participationRepository) {
        this.campaignRepository = campaignRepository;
        this.participationRepository = participationRepository;
    }

    public Campaign createCampaign(String name, String description, LocalDate startDate, 
                                 LocalDate endDate, BigDecimal budget) {
        Campaign campaign = new Campaign();
        campaign.setName(name);
        campaign.setDescription(description);
        campaign.setStartDate(startDate);
        campaign.setEndDate(endDate);
        campaign.setBudget(budget);
        campaign.setActive(true);
        campaign.setCreatedAt(LocalDateTime.now());
        
        return campaignRepository.save(campaign);
    }

    @Transactional(readOnly = true)
    public List<Campaign> getActiveCampaigns() {
        LocalDateTime now = LocalDateTime.now();
        return campaignRepository.findAll().stream()
                .filter(this::isCampaignCurrentlyActive)
                .toList();
    }

    public CampaignParticipation participateInCampaign(Long campaignId, String userId, BigDecimal amount) {
        Campaign campaign = campaignRepository.findById(campaignId)
                .orElseThrow(() -> new CampaignNotFoundException("Campaign not found with id: " + campaignId));

        validateCampaignEligibility(campaign);

        CampaignParticipation participation = new CampaignParticipation();
        participation.setCampaign(campaign);
        participation.setUserId(userId);
        participation.setAmount(amount);
        participation.setParticipatedAt(LocalDateTime.now());

        return participationRepository.save(participation);
    }

    @Transactional(readOnly = true)
    public BigDecimal calculateTotalParticipation(Long campaignId) {
        return participationRepository.findByCampaignId(campaignId).stream()
                .map(CampaignParticipation::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public void deactivateCampaign(Long campaignId) {
        Campaign campaign = campaignRepository.findById(campaignId)
                .orElseThrow(() -> new CampaignNotFoundException("Campaign not found with id: " + campaignId));
        
        campaign.setActive(false);
        campaignRepository.save(campaign);
    }

    private void validateCampaignEligibility(Campaign campaign) {
        if (!campaign.isActive()) {
            throw new CampaignNotActiveException("Campaign is not active");
        }

        if (!isCampaignCurrentlyActive(campaign)) {
            throw new CampaignNotActiveException("Campaign is not within valid date range");
        }

        BigDecimal totalParticipation = calculateTotalParticipation(campaign.getId());
        if (totalParticipation.compareTo(campaign.getBudget()) >= 0) {
            throw new CampaignNotActiveException("Campaign budget has been exceeded");
        }
    }

    private boolean isCampaignCurrentlyActive(Campaign campaign) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime startDateTime = campaign.getStartDate().atStartOfDay();
        
        boolean afterStart = !now.isBefore(startDateTime);
        boolean beforeEnd = now.isBefore(campaign.getEndDate().atStartOfDay());
        
        return afterStart && beforeEnd;
    }

    @Transactional(readOnly = true)
    public Optional<Campaign> findCampaignById(Long campaignId) {
        return campaignRepository.findById(campaignId);
    }

    @Transactional(readOnly = true)
    public List<CampaignParticipation> getCampaignParticipations(Long campaignId) {
        return participationRepository.findByCampaignId(campaignId);
    }
}