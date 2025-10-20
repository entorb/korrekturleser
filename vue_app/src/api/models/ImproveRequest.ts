/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Text improvement request schema.
 */
export type ImproveRequest = {
    /**
     * Text to improve
     */
    text: string;
    /**
     * Improvement mode
     */
    mode: ImproveRequest.mode;
};
export namespace ImproveRequest {
    /**
     * Improvement mode
     */
    export enum mode {
        CORRECT = 'correct',
        IMPROVE = 'improve',
        SUMMARIZE = 'summarize',
        EXPAND = 'expand',
        TRANSLATE_DE = 'translate_de',
        TRANSLATE_EN = 'translate_en',
    }
}

