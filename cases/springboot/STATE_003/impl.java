package com.example.inventory.service;

import com.example.inventory.entity.Product;
import com.example.inventory.entity.StockReservation;
import com.example.inventory.exception.InsufficientStockException;
import com.example.inventory.exception.ProductNotFoundException;
import com.example.inventory.repository.ProductRepository;
import com.example.inventory.repository.StockReservationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Service
public class StockReservationService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private StockReservationRepository stockReservationRepository;

    @Transactional
    public StockReservation reserveStock(Long productId, Integer quantity, String customerId) {
        validateReservationRequest(productId, quantity, customerId);
        
        Product product = findProductById(productId);
        
        if (product.getStockQuantity() >= quantity) {
            product.setStockQuantity(product.getStockQuantity() - quantity);
            productRepository.save(product);
            
            return createStockReservation(product, quantity, customerId);
        } else {
            throw new InsufficientStockException(
                String.format("Insufficient stock for product %d. Available: %d, Requested: %d", 
                    productId, product.getStockQuantity(), quantity)
            );
        }
    }

    @Transactional
    public void releaseReservation(String reservationId) {
        Optional<StockReservation> reservationOpt = stockReservationRepository.findByReservationId(reservationId);
        
        if (reservationOpt.isPresent()) {
            StockReservation reservation = reservationOpt.get();
            Product product = reservation.getProduct();
            
            product.setStockQuantity(product.getStockQuantity() + reservation.getQuantity());
            productRepository.save(product);
            
            reservation.setStatus("RELEASED");
            reservation.setReleasedAt(LocalDateTime.now());
            stockReservationRepository.save(reservation);
        }
    }

    @Transactional(readOnly = true)
    public BigDecimal calculateReservationValue(String reservationId) {
        StockReservation reservation = stockReservationRepository.findByReservationId(reservationId)
            .orElseThrow(() -> new IllegalArgumentException("Reservation not found: " + reservationId));
        
        return reservation.getProduct().getPrice().multiply(BigDecimal.valueOf(reservation.getQuantity()));
    }

    private void validateReservationRequest(Long productId, Integer quantity, String customerId) {
        if (productId == null || productId <= 0) {
            throw new IllegalArgumentException("Product ID must be positive");
        }
        if (quantity == null || quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        if (customerId == null || customerId.trim().isEmpty()) {
            throw new IllegalArgumentException("Customer ID cannot be empty");
        }
    }

    private Product findProductById(Long productId) {
        return productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException("Product not found with ID: " + productId));
    }

    private StockReservation createStockReservation(Product product, Integer quantity, String customerId) {
        StockReservation reservation = new StockReservation();
        reservation.setReservationId(UUID.randomUUID().toString());
        reservation.setProduct(product);
        reservation.setQuantity(quantity);
        reservation.setCustomerId(customerId);
        reservation.setStatus("ACTIVE");
        reservation.setCreatedAt(LocalDateTime.now());
        reservation.setExpiresAt(LocalDateTime.now().plusHours(24));
        
        return stockReservationRepository.save(reservation);
    }

    @Transactional(readOnly = true)
    public boolean isStockAvailable(Long productId, Integer quantity) {
        Product product = findProductById(productId);
        return product.getStockQuantity() >= quantity;
    }
}