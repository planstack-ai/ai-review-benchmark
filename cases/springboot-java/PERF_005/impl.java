package com.example.ecommerce.service;

import com.example.ecommerce.entity.Customer;
import com.example.ecommerce.repository.CustomerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Service
public class CustomerSearchService {

    @Autowired
    private CustomerRepository customerRepository;

    @Transactional(readOnly = true)
    public Optional<Customer> findByEmail(String email) {
        return customerRepository.findByEmail(email);
    }

    @Transactional(readOnly = true)
    public List<Customer> findByPhoneNumber(String phoneNumber) {
        String normalizedPhone = normalizePhoneNumber(phoneNumber);
        return customerRepository.findByPhoneNumber(normalizedPhone);
    }

    @Transactional(readOnly = true)
    public List<Customer> searchByName(String searchTerm) {
        return customerRepository.findByLastNameContaining(searchTerm);
    }

    @Transactional(readOnly = true)
    public List<Customer> advancedSearch(String email, String phone, String name) {
        List<Customer> results = new ArrayList<>();

        if (email != null && !email.isEmpty()) {
            customerRepository.findByEmail(email).ifPresent(results::add);
        }

        if (phone != null && !phone.isEmpty()) {
            results.addAll(customerRepository.findByPhoneNumber(normalizePhoneNumber(phone)));
        }

        if (name != null && !name.isEmpty()) {
            results.addAll(customerRepository.findByLastNameContaining(name));
        }

        return results.stream().distinct().toList();
    }

    @Transactional(readOnly = true)
    public Customer findCustomerForSupport(String identifier) {
        Optional<Customer> byEmail = customerRepository.findByEmail(identifier);
        if (byEmail.isPresent()) {
            return byEmail.get();
        }

        List<Customer> byPhone = customerRepository.findByPhoneNumber(identifier);
        if (!byPhone.isEmpty()) {
            return byPhone.get(0);
        }

        List<Customer> byName = customerRepository.findByLastNameContaining(identifier);
        if (!byName.isEmpty()) {
            return byName.get(0);
        }

        return null;
    }

    private String normalizePhoneNumber(String phone) {
        if (phone == null) {
            return null;
        }
        return phone.replaceAll("[^0-9+]", "");
    }
}
