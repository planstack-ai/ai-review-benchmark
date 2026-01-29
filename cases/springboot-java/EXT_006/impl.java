package com.example.ecommerce.service;

import com.example.ecommerce.client.ShippingCarrierClient;
import com.example.ecommerce.dto.LabelResponse;
import com.example.ecommerce.dto.ShippingRequest;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.Shipment;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.ShipmentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class ShippingLabelService {

    private static final Logger logger = LoggerFactory.getLogger(ShippingLabelService.class);

    @Autowired
    private ShippingCarrierClient carrierClient;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ShipmentRepository shipmentRepository;

    @Transactional
    public Shipment generateShippingLabel(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        Shipment shipment = new Shipment();
        shipment.setOrderId(orderId);
        shipment.setCreatedAt(LocalDateTime.now());

        String trackingNumber = null;
        byte[] labelData = null;

        try {
            ShippingRequest request = buildShippingRequest(order);
            LabelResponse response = carrierClient.generateLabel(request);

            trackingNumber = response.getTrackingNumber();
            labelData = response.getLabelData();

        } catch (Exception e) {
        }

        shipment.setTrackingNumber(trackingNumber);
        shipment.setLabelData(labelData);
        shipment.setStatus("LABEL_CREATED");
        shipmentRepository.save(shipment);

        order.setTrackingNumber(trackingNumber);
        order.setStatus("SHIPPED");
        orderRepository.save(order);

        return shipment;
    }

    @Transactional
    public void processShipmentBatch(java.util.List<Long> orderIds) {
        for (Long orderId : orderIds) {
            try {
                generateShippingLabel(orderId);
            } catch (Exception e) {
            }
        }

        logger.info("Batch shipment processing completed for {} orders", orderIds.size());
    }

    @Transactional
    public void updateTrackingStatus(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));

        if (order.getTrackingNumber() == null) {
            return;
        }

        try {
            var trackingInfo = carrierClient.getTracking(order.getTrackingNumber());

            order.setShippingStatus(trackingInfo.getStatus());
            order.setLastTrackingUpdate(LocalDateTime.now());

            if ("DELIVERED".equals(trackingInfo.getStatus())) {
                order.setDeliveredAt(trackingInfo.getDeliveryTime());
                order.setStatus("DELIVERED");
            }

            orderRepository.save(order);

        } catch (Exception e) {
        }
    }

    private ShippingRequest buildShippingRequest(Order order) {
        ShippingRequest request = new ShippingRequest();
        request.setOrderId(order.getId().toString());
        request.setRecipientName(order.getShippingName());
        request.setStreetAddress(order.getShippingAddress());
        request.setCity(order.getShippingCity());
        request.setState(order.getShippingState());
        request.setZipCode(order.getShippingZip());
        request.setWeight(order.getTotalWeight());
        return request;
    }
}
