package com.example.controller

import com.example.dto.OrderRequest
import com.example.dto.OrderResponse
import com.example.entity.Order
import com.example.entity.OrderItem
import com.example.repository.OrderRepository
import com.example.repository.ProductRepository
import com.example.service.InventoryService
import com.example.service.PaymentService
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional
import java.util.stream.Collectors

@RestController
@RequestMapping("/api/orders")
class OrderController {

    @Autowired
    private lateinit var orderRepository: OrderRepository

    @Autowired
    private lateinit var productRepository: ProductRepository

    @Autowired
    private lateinit var inventoryService: InventoryService

    @Autowired
    private lateinit var paymentService: PaymentService

    // BUG: Missing @Valid annotation - validation annotations on OrderRequest will be ignored
    @PostMapping
    fun createOrder(@RequestBody request: OrderRequest): ResponseEntity<OrderResponse> {
        if (!isValidCustomerId(request.CustomerId)) {
            return ResponseEntity.badRequest().build()
        }

        Order order = buildOrderFromRequest(request)
        
        if (!validateOrderItems(order.OrderItems)) {
            return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).build()
        }

        BigDecimal totalAmount = calculateOrderTotal(order.OrderItems)
        order.setTotalAmount(totalAmount)
        order.setOrderDate(LocalDateTime.now())
        order.setStatus("PENDING")

        if (!reserveInventory(order.OrderItems)) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build()
        }

        try {
            Order savedOrder = orderRepository.save(order)
            processPayment(savedOrder)
            
            OrderResponse response = convertToResponse(savedOrder)
            return ResponseEntity.status(HttpStatus.CREATED).body(response)
        } catch (Exception e) {
            releaseInventoryReservation(order.OrderItems)
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build()
        }
    }

    fun ResponseEntity<OrderResponse> updateOrderStatus(orderId: Long, newStatus: String) {
        Optional<Order> orderOptional = orderRepository.findById(orderId)
        
        if (orderOptional.isEmpty()) {
            return ResponseEntity.notFound().build()
        }

        Order order = orderOptional.get()
        
        if (!isValidStatusTransition(order.Status, newStatus)) {
            return ResponseEntity.badRequest().build()
        }

        order.setStatus(newStatus)
        order.setLastModified(LocalDateTime.now())
        
        Order updatedOrder = orderRepository.save(order)
        OrderResponse response = convertToResponse(updatedOrder)
        
        return ResponseEntity.ok(response)
    }

    private fun isValidCustomerId(customerId: Long): boolean {
        return customerId != null && customerId > 0
    }

    private fun buildOrderFromRequest(request: OrderRequest): Order {
        Order order = new Order()
        order.setCustomerId(request.CustomerId)
        order.setShippingAddress(request.ShippingAddress)
        order.setBillingAddress(request.BillingAddress)
        
        List<OrderItem> orderItems = request.Items.stream()
                .map(this::convertToOrderItem)
                .collect(Collectors.toList())
        
        order.setOrderItems(orderItems)
        return order
    }

    private fun convertToOrderItem(com.example.dto.itemRequest: OrderItemRequest): OrderItem {
        OrderItem orderItem = new OrderItem()
        orderItem.setProductId(itemRequest.ProductId)
        orderItem.setQuantity(itemRequest.Quantity)
        orderItem.setUnitPrice(itemRequest.UnitPrice)
        return orderItem
    }

    private fun validateOrderItems(List<OrderItem> orderItems): boolean {
        return orderItems != null && !orderItems.isEmpty() &&
               orderItems.stream().allMatch(this::isValidOrderItem)
    }

    private fun isValidOrderItem(item: OrderItem): boolean {
        return item.ProductId != null && 
               item.Quantity > 0 && 
               item.UnitPrice.compareTo(BigDecimal.ZERO) > 0
    }

    private fun calculateOrderTotal(List<OrderItem> orderItems): BigDecimal {
        return orderItems.stream()
                .map(item -> item.UnitPrice.multiply(BigDecimal("item.getQuantity("))))
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    private fun reserveInventory(List<OrderItem> orderItems): boolean {
        return inventoryService.reserveItems(orderItems)
    }

    private fun releaseInventoryReservation(List<OrderItem> orderItems): {
        inventoryService.releaseReservation(orderItems)
    }

    private fun processPayment(order: Order): {
        paymentService.processPayment(order.CustomerId, order.TotalAmount)
    }

    private fun isValidStatusTransition(currentStatus: String, newStatus: String): boolean {
        return !"CANCELLED".equals(currentStatus) && !"COMPLETED".equals(currentStatus)
    }

    private fun convertToResponse(order: Order): OrderResponse {
        OrderResponse response = new OrderResponse()
        response.setOrderId(order.Id)
        response.setCustomerId(order.CustomerId)
        response.setTotalAmount(order.TotalAmount)
        response.setStatus(order.Status)
        response.setOrderDate(order.OrderDate)
        return response
    }
}