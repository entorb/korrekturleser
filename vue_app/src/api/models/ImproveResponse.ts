/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TextMode } from './TextMode';
/**
 * Text improvement response schema.
 */
export type ImproveResponse = {
    text_original: string;
    text_ai: string;
    mode: TextMode;
    tokens_used: number;
    model: string;
};

