/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoginRequest } from '../models/LoginRequest';
import type { TokenResponse } from '../models/TokenResponse';
import type { UserInfoResponse } from '../models/UserInfoResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Login
     * Authenticate user with secret and return JWT token.
     *
     * Rate limit: 5 login attempts per minute per IP address.
     *
     * Args:
     * request: FastAPI request object (for rate limiting)
     * login_request: Login credentials containing secret
     *
     * Returns:
     * TokenResponse: JWT token and user information
     *
     * Raises:
     * HTTPException: If credentials are invalid or rate limit exceeded
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public static loginApiAuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Me
     * Get current authenticated user information including usage statistics.
     *
     * Args:
     * current_user: Injected by dependency
     *
     * Returns:
     * UserInfoResponse: Current user information with usage stats (without user_id)
     * @returns UserInfoResponse Successful Response
     * @throws ApiError
     */
    public static getMeApiAuthMeGet(): CancelablePromise<UserInfoResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/auth/me',
        });
    }
}
