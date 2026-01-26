package com.example.ecommerce.service;

import com.example.ecommerce.entity.Cart;
import com.example.ecommerce.entity.CartItem;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.entity.User;
import com.example.ecommerce.repository.CartRepository;
import com.example.ecommerce.repository.CartItemRepository;
import com.example.ecommerce.repository.ProductRepository;
import com.example.ecommerce.exception.CartNotFoundException;
import com.example.ecommerce.exception.ProductNotFoundException;
import com.example.ecommerce.exception.InsufficientStockException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Optional;

@Service
@Transactional
public class CartService {

    @Autowired
    private CartRepository cartRepository;

    @Autowired
    private CartItemRepository cartItemRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserService userService;

    public Cart addItemToCart(Long cartId, Long productId, Integer quantity) {
        Cart cart = findCartById(cartId);
        Product product = findProductById(productId);
        
        validateStockAvailability(product, quantity);
        
        Optional<CartItem> existingItem = findExistingCartItem(cart, product);
        
        if (existingItem.isPresent()) {
            updateExistingCartItem(existingItem.get(), quantity);
        } else {
            createNewCartItem(cart, product, quantity);
        }
        
        updateCartTotal(cart);
        return cartRepository.save(cart);
    }

    public Cart removeItemFromCart(Long cartId, Long productId) {
        Cart cart = findCartById(cartId);
        
        CartItem itemToRemove = cart.getItems().stream()
            .filter(item -> item.getProduct().getId().equals(productId))
            .findFirst()
            .orElseThrow(() -> new CartNotFoundException("Item not found in cart"));
            
        cart.getItems().remove(itemToRemove);
        cartItemRepository.delete(itemToRemove);
        
        updateCartTotal(cart);
        return cartRepository.save(cart);
    }

    public Cart updateItemQuantity(Long cartId, Long productId, Integer newQuantity) {
        Cart cart = findCartById(cartId);
        Product product = findProductById(productId);
        
        validateStockAvailability(product, newQuantity);
        
        CartItem cartItem = cart.getItems().stream()
            .filter(item -> item.getProduct().getId().equals(productId))
            .findFirst()
            .orElseThrow(() -> new CartNotFoundException("Item not found in cart"));
            
        cartItem.setQuantity(newQuantity);
        cartItem.setSubtotal(calculateItemSubtotal(product.getPrice(), newQuantity));
        
        updateCartTotal(cart);
        return cartRepository.save(cart);
    }

    public void clearCart(Long cartId) {
        Cart cart = findCartById(cartId);
        cart.getItems().clear();
        cart.setTotalAmount(BigDecimal.ZERO);
        cartRepository.save(cart);
    }

    private Cart findCartById(Long cartId) {
        return cartRepository.findById(cartId)
            .orElseThrow(() -> new CartNotFoundException("Cart not found with id: " + cartId));
    }

    private Product findProductById(Long productId) {
        return productRepository.findById(productId)
            .orElseThrow(() -> new ProductNotFoundException("Product not found with id: " + productId));
    }

    private void validateStockAvailability(Product product, Integer requestedQuantity) {
        if (product.getStockQuantity() < requestedQuantity) {
            throw new InsufficientStockException("Insufficient stock for product: " + product.getName());
        }
    }

    private Optional<CartItem> findExistingCartItem(Cart cart, Product product) {
        return cart.getItems().stream()
            .filter(item -> item.getProduct().getId().equals(product.getId()))
            .findFirst();
    }

    private void updateExistingCartItem(CartItem cartItem, Integer additionalQuantity) {
        Integer newQuantity = cartItem.getQuantity() + additionalQuantity;
        cartItem.setQuantity(newQuantity);
        cartItem.setSubtotal(calculateItemSubtotal(cartItem.getProduct().getPrice(), newQuantity));
    }

    private void createNewCartItem(Cart cart, Product product, Integer quantity) {
        CartItem newItem = new CartItem();
        newItem.setCart(cart);
        newItem.setProduct(product);
        newItem.setQuantity(quantity);
        newItem.setSubtotal(calculateItemSubtotal(product.getPrice(), quantity));
        cart.getItems().add(newItem);
    }

    private BigDecimal calculateItemSubtotal(BigDecimal unitPrice, Integer quantity) {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }

    private void updateCartTotal(Cart cart) {
        BigDecimal total = cart.getItems().stream()
            .map(CartItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        cart.setTotalAmount(total);
    }
}