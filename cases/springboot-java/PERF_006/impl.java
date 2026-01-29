package com.example.ecommerce.service;

import com.example.ecommerce.entity.User;
import com.example.ecommerce.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class UserProfileService {

    @Autowired
    private UserRepository userRepository;

    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    public Map<String, Object> getUserProfile(Long userId) {
        Optional<User> userOpt = userRepository.findById(userId);
        if (userOpt.isEmpty()) {
            return null;
        }

        User user = userOpt.get();
        Map<String, Object> profile = new HashMap<>();
        profile.put("id", user.getId());
        profile.put("email", user.getEmail());
        profile.put("firstName", user.getFirstName());
        profile.put("lastName", user.getLastName());
        profile.put("phone", user.getPhone());
        profile.put("address", user.getAddress());

        return profile;
    }

    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    public User getUser(Long userId) {
        return userRepository.findById(userId).orElse(null);
    }

    @CacheEvict(value = "userProfile", allEntries = true)
    @Transactional
    public User updateUserProfile(Long userId, Map<String, String> updates) {
        Optional<User> userOpt = userRepository.findById(userId);
        if (userOpt.isEmpty()) {
            throw new IllegalArgumentException("User not found: " + userId);
        }

        User user = userOpt.get();

        if (updates.containsKey("firstName")) {
            user.setFirstName(updates.get("firstName"));
        }
        if (updates.containsKey("lastName")) {
            user.setLastName(updates.get("lastName"));
        }
        if (updates.containsKey("phone")) {
            user.setPhone(updates.get("phone"));
        }
        if (updates.containsKey("address")) {
            user.setAddress(updates.get("address"));
        }

        return userRepository.save(user);
    }

    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    public Map<String, Object> getUserPreferences(Long userId) {
        User user = userRepository.findById(userId).orElse(null);
        if (user == null) {
            return new HashMap<>();
        }

        Map<String, Object> preferences = new HashMap<>();
        preferences.put("userId", user.getId());
        preferences.put("notificationsEnabled", true);
        preferences.put("theme", "light");
        preferences.put("language", "en");

        return preferences;
    }
}
