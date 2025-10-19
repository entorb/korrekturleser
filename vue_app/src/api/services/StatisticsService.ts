/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UsageStatsResponse } from '../models/UsageStatsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StatisticsService {
    /**
     * Get Usage Stats
     * Get usage statistics (daily and total).
     *
     * Only available in PROD environment and only for user_id=1 (admin).
     *
     * Args:
     * current_user: Authenticated user (injected by dependency)
     *
     * Returns:
     * UsageStatsResponse: Daily and total usage statistics
     *
     * Raises:
     * HTTPException: If not in PROD or user is not admin
     * @returns UsageStatsResponse Successful Response
     * @throws ApiError
     */
    public static getUsageStatsApiStatsGet(): CancelablePromise<UsageStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stats/',
        });
    }
    /**
     * Get My Usage
     * Get current user's usage statistics.
     *
     * Args:
     * current_user: Authenticated user (injected by dependency)
     *
     * Returns:
     * Dictionary with user's request and token counts
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMyUsageApiStatsMyUsageGet(): CancelablePromise<Record<string, (number | string)>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stats/my-usage',
        });
    }
}
