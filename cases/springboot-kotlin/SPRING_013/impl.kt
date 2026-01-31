package com.example.order.controller

import com.example.order.entity.Order
import com.example.order.service.OrderService
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotEmpty
import jakarta.validation.constraints.Positive
import org.springframework.http.HttpStatus
import org.springframework.validation.annotation.Validated
import org.springframework.web.bind.annotation.*
import java.math.BigDecimal

data class OrderRequest(
    @field:NotBlank(message = "Customer email is required")
    val customerEmail: String,

    // BUG: Missing @Valid annotation on nested list
    // Validation annotations in OrderItemRequest will be ignored
    // Invalid items (blank product name, negative quantity/price) will pass validation
    @field:NotEmpty(message = "Order must contain at least one item")
    val items: List<OrderItemRequest>
)

data class OrderItemRequest(
    @field:NotBlank(message = "Product name is required")
    val productName: String,

    @field:Positive(message = "Quantity must be positive")
    val quantity: Int,

    @field:Positive(message = "Price must be positive")
    val price: BigDecimal
)

data class OrderResponse(
    val id: Long,
    val customerEmail: String,
    val totalAmount: BigDecimal,
    val status: String
)

@RestController
@RequestMapping("/api/orders")
@Validated
class OrderController(
    private val orderService: OrderService
) {

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun createOrder(@Valid @RequestBody request: OrderRequest): OrderResponse {
        val order = orderService.createOrder(request)

        return OrderResponse(
            id = order.id!!,
            customerEmail = order.customerEmail,
            totalAmount = order.totalAmount,
            status = order.status
        )
    }
}
