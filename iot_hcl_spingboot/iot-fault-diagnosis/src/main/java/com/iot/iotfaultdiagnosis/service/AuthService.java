package com.iot.iotfaultdiagnosis.service;

import com.iot.iotfaultdiagnosis.dto.auth.AuthResponse;
import com.iot.iotfaultdiagnosis.dto.auth.LoginRequest;
import com.iot.iotfaultdiagnosis.dto.auth.RegisterRequest;
import com.iot.iotfaultdiagnosis.dto.auth.UserResponse;
import com.iot.iotfaultdiagnosis.entity.Role;
import com.iot.iotfaultdiagnosis.entity.UserEntity;
import com.iot.iotfaultdiagnosis.exception.UserAlreadyExistsException;
import com.iot.iotfaultdiagnosis.repository.UserRepository;
import com.iot.iotfaultdiagnosis.security.JwtTokenProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;

    public AuthService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       AuthenticationManager authenticationManager,
                       JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.tokenProvider = tokenProvider;
    }

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        log.info("Attempting registration for username: {}, email: {}", request.getUsername(), request.getEmail());

        if (userRepository.existsByUsername(request.getUsername())) {
            throw new UserAlreadyExistsException("Username '" + request.getUsername() + "' is already registered");
        }

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Email '" + request.getEmail() + "' is already registered");
        }

        Role role = request.getRole() != null ? request.getRole() : Role.USER;
        String passwordHash = passwordEncoder.encode(request.getPassword());

        UserEntity user = new UserEntity(
                request.getUsername(),
                request.getEmail(),
                passwordHash,
                role,
                LocalDateTime.now()
        );

        userRepository.save(user);
        log.info("User successfully registered: {}", user.getUsername());

        String token = tokenProvider.generateToken(user.getUsername(), user.getRole().name());

        return new AuthResponse(
                token,
                user.getUsername(),
                user.getEmail(),
                user.getRole().name(),
                tokenProvider.getExpirationSeconds()
        );
    }

    public AuthResponse login(LoginRequest request) {
        log.info("Login attempt for identifier: {}", request.getUsername());

        // Find user by username or email first to resolve standard username for auth manager
        UserEntity user = userRepository.findByUsernameOrEmail(request.getUsername(), request.getUsername())
                .orElseThrow(() -> new BadCredentialsException("Invalid username or password"));

        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(user.getUsername(), request.getPassword())
            );

            String token = tokenProvider.generateToken(user.getUsername(), user.getRole().name());

            return new AuthResponse(
                    token,
                    user.getUsername(),
                    user.getEmail(),
                    user.getRole().name(),
                    tokenProvider.getExpirationSeconds()
            );
        } catch (BadCredentialsException e) {
            log.warn("Invalid password for user: {}", user.getUsername());
            throw new BadCredentialsException("Invalid username or password");
        }
    }

    public UserResponse getCurrentUser(String username) {
        UserEntity user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));

        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getRole().name(),
                user.getCreatedAt()
        );
    }
}
