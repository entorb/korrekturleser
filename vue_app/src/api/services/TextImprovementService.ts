/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ImproveRequest } from '../models/ImproveRequest';
import type { ImproveResponse } from '../models/ImproveResponse';
import type { ModesResponse } from '../models/ModesResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TextImprovementService {
    /**
     * Improve Text
     * Improve text using AI based on the selected mode.
     *
     * Args:
     * request: Text improvement request with text and mode
     * current_user: Authenticated user (injected by dependency)
     *
     * Returns:
     * ImproveResponse: Improved text and metadata
     *
     * Raises:
     * HTTPException: If LLM processing fails
     * @param requestBody
     * @returns ImproveResponse Successful Response
     * @throws ApiError
     */
    public static improveTextApiTextPost(
        requestBody: ImproveRequest,
    ): CancelablePromise<ImproveResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/text/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Modes
     * Get available improvement modes.
     *
     * Returns:
     * ModesResponse with available modes and descriptions
     * @returns ModesResponse Successful Response
     * @throws ApiError
     */
    public static getModesApiTextModesGet(): CancelablePromise<ModesResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/text/modes',
        });
    }
}
