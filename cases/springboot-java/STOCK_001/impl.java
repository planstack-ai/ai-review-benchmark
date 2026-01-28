package com.example.inventory.service;

import com.example.inventory.entity.Stock;
import com.example.inventory.entity.ReservationRequest;
import com.example.inventory.entity.ReservationResult;
import com.example.inventory.repository.StockRepository;
import com.example.inventory.exception.InsufficientStockException;
import com.example.inventory.exception.ProductNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
@Transactional
public class StockReservationService {

    @Autowired
    private StockRepository stockRepository;

    public ReservationResult reserveStock(ReservationRequest request) {
        validateReservationRequest(request);
        
        Stock stock = findStockByProductId(request.getProductId());
        
        if (canReserveQuantity(stock, request.getQuantity())) {
            performStockReservation(stock, request.getQuantity());
            return createSuccessfulReservation(request, stock);
        } else {
            throw new InsufficientStockException(
                "Insufficient stock for product: " + request.getProductId() + 
                ". Available: " + stock.getQuantity() + ", Requested: " + request.getQuantity()
            );
        }
    }

    private void validateReservationRequest(ReservationRequest request) {
        if (request == null) {
            throw new IllegalArgumentException("Reservation request cannot be null");
        }
        if (request.getProductId() == null || request.getProductId().trim().isEmpty()) {
            throw new IllegalArgumentException("Product ID cannot be null or empty");
        }
        if (request.getQuantity() <= 0) {
            throw new IllegalArgumentException("Quantity must be greater than zero");
        }
    }

    private Stock findStockByProductId(String productId) {
        Optional<Stock> stockOptional = stockRepository.findByProductId(productId);
        return stockOptional.orElseThrow(() -> 
            new ProductNotFoundException("Product not found: " + productId)
        );
    }

    private boolean canReserveQuantity(Stock stock, Integer requestedQuantity) {
        return stock.getQuantity() >= requestedQuantity && stock.isActive();
    }

    private void performStockReservation(Stock stock, Integer quantity) {
        if (stock.getQuantity() >= quantity) {
            stock.setQuantity(stock.getQuantity() - quantity);
            stock.setLastModified(LocalDateTime.now());
            stockRepository.save(stock);
        }
    }

    private ReservationResult createSuccessfulReservation(ReservationRequest request, Stock stock) {
        ReservationResult result = new ReservationResult();
        result.setProductId(request.getProductId());
        result.setReservedQuantity(request.getQuantity());
        result.setRemainingStock(stock.getQuantity());
        result.setReservationTime(LocalDateTime.now());
        result.setSuccess(true);
        return result;
    }

    public Integer getAvailableStock(String productId) {
        Stock stock = findStockByProductId(productId);
        return stock.getQuantity();
    }

    public void releaseReservation(String productId, Integer quantity) {
        Stock stock = findStockByProductId(productId);
        stock.setQuantity(stock.getQuantity() + quantity);
        stock.setLastModified(LocalDateTime.now());
        stockRepository.save(stock);
    }

    private BigDecimal calculateReservationValue(Stock stock, Integer quantity) {
        return stock.getUnitPrice().multiply(BigDecimal.valueOf(quantity));
    }
}