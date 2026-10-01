package com.iot.iotfaultdiagnosis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iot.iotfaultdiagnosis.dto.auth.LoginRequest;
import com.iot.iotfaultdiagnosis.dto.auth.RegisterRequest;
import com.iot.iotfaultdiagnosis.entity.Role;
import com.iot.iotfaultdiagnosis.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class AuthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private com.iot.iotfaultdiagnosis.service.DiagnosisStore diagnosisStore;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
        diagnosisStore.clear();
    }

    @Test
    void testRegister_Success() throws Exception {
        RegisterRequest request = new RegisterRequest("testuser", "test@iot.com", "secret123", Role.USER);

        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.token").isNotEmpty())
                .andExpect(jsonPath("$.tokenType").value("Bearer"))
                .andExpect(jsonPath("$.username").value("testuser"))
                .andExpect(jsonPath("$.email").value("test@iot.com"))
                .andExpect(jsonPath("$.role").value("USER"));

        // Verify password is encrypted in database
        var userInDb = userRepository.findByUsername("testuser");
        assertThat(userInDb).isPresent();
        assertThat(userInDb.get().getPasswordHash()).doesNotContain("secret123");
        assertThat(userInDb.get().getPasswordHash()).startsWith("$2a$");
    }

    @Test
    void testRegister_DuplicateUsername() throws Exception {
        RegisterRequest first = new RegisterRequest("alice", "alice@iot.com", "secret123", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(first)))
                .andExpect(status().isCreated());

        RegisterRequest duplicate = new RegisterRequest("alice", "another@iot.com", "secret123", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(duplicate)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.status").value(409))
                .andExpect(jsonPath("$.error").value("Conflict"))
                .andExpect(jsonPath("$.message").value("Username 'alice' is already registered"));
    }

    @Test
    void testRegister_DuplicateEmail() throws Exception {
        RegisterRequest first = new RegisterRequest("bob1", "bob@iot.com", "secret123", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(first)))
                .andExpect(status().isCreated());

        RegisterRequest duplicate = new RegisterRequest("bob2", "bob@iot.com", "secret123", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(duplicate)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.status").value(409))
                .andExpect(jsonPath("$.message").value("Email 'bob@iot.com' is already registered"));
    }

    @Test
    void testRegister_InvalidInputShortPassword() throws Exception {
        RegisterRequest request = new RegisterRequest("charlie", "charlie@iot.com", "123", Role.USER);

        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    void testLogin_SuccessWithUsername() throws Exception {
        // First register
        RegisterRequest reg = new RegisterRequest("operator1", "op1@iot.com", "password456", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated());

        // Login with username
        LoginRequest login = new LoginRequest("operator1", "password456");
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(login)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isNotEmpty())
                .andExpect(jsonPath("$.username").value("operator1"))
                .andExpect(jsonPath("$.role").value("USER"));
    }

    @Test
    void testLogin_SuccessWithEmail() throws Exception {
        // Register admin
        RegisterRequest reg = new RegisterRequest("adminuser", "admin@iot.com", "adminpass", Role.ADMIN);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated());

        // Login with email
        LoginRequest login = new LoginRequest("admin@iot.com", "adminpass");
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(login)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isNotEmpty())
                .andExpect(jsonPath("$.username").value("adminuser"))
                .andExpect(jsonPath("$.role").value("ADMIN"));
    }

    @Test
    void testLogin_InvalidPassword() throws Exception {
        RegisterRequest reg = new RegisterRequest("dave", "dave@iot.com", "correctpass", Role.USER);
        mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated());

        LoginRequest login = new LoginRequest("dave", "wrongpass");
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(login)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status").value(401))
                .andExpect(jsonPath("$.message").value("Invalid username or password"));
    }

    @Test
    void testLogin_NonExistentUser() throws Exception {
        LoginRequest login = new LoginRequest("ghost", "anypassword");
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(login)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status").value(401));
    }

    @Test
    void testProtectedEndpoint_UnauthorizedWithoutToken() throws Exception {
        mockMvc.perform(get("/api/v1/diagnosis/latest"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.status").value(401))
                .andExpect(jsonPath("$.error").value("Unauthorized"));
    }

    @Test
    void testProtectedEndpoint_AuthorizedWithValidToken() throws Exception {
        // 1. Register user
        RegisterRequest reg = new RegisterRequest("engineer", "eng@iot.com", "engpass123", Role.USER);
        MvcResult regResult = mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated())
                .andReturn();

        String responseBody = regResult.getResponse().getContentAsString();
        String token = objectMapper.readTree(responseBody).path("token").asText();

        // 2. Access protected endpoint with Bearer token
        mockMvc.perform(get("/api/v1/diagnosis/latest")
                        .header("Authorization", "Bearer " + token))
                // Returns 404 because store is empty, but is authenticated (NOT 401)
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetCurrentUser_Success() throws Exception {
        RegisterRequest reg = new RegisterRequest("sarah", "sarah@iot.com", "sarahpass", Role.USER);
        MvcResult regResult = mockMvc.perform(post("/api/v1/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reg)))
                .andExpect(status().isCreated())
                .andReturn();

        String token = objectMapper.readTree(regResult.getResponse().getContentAsString()).path("token").asText();

        mockMvc.perform(get("/api/v1/auth/me")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("sarah"))
                .andExpect(jsonPath("$.email").value("sarah@iot.com"))
                .andExpect(jsonPath("$.role").value("USER"));
    }

    @Test
    void testGetCurrentUser_Unauthorized() throws Exception {
        mockMvc.perform(get("/api/v1/auth/me"))
                .andExpect(status().isUnauthorized());
    }
}
