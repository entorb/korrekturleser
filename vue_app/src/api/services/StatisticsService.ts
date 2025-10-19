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
     * Get All Users Stats
     * Get usage statistics for all users (daily and total).
     *
     * Only available for user_id=1 (admin).
     * - PROD: Queries database and returns data with all values set to 0
     * - Local: Returns mock data for user Torben with all values set to 0
     *
     * Args:
     * current_user: Authenticated user (injected by dependency)
     *
     * Returns:
     * UsageStatsResponse: Daily and total usage statistics
     *
     * Raises:
     * HTTPException: If user is not admin
     * @returns UsageStatsResponse Successful Response
     * @throws ApiError
     */
    public static getAllUsersStatsApiStatsAllUsersGet(): CancelablePromise<UsageStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/stats/all-users',
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
