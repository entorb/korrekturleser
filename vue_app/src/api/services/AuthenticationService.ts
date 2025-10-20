/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoginRequest } from '../models/LoginRequest';
import type { TokenResponse } from '../models/TokenResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthenticationService {
    /**
     * Login
     * Authenticate user with secret and return JWT token.
     *
     * Rate limited
     *
     * Args:
     * request: FastAPI request object (for rate limiting)
     * login_request: Login credentials containing secret
     *
     * Returns:
     * TokenResponse: JWT token
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
}
