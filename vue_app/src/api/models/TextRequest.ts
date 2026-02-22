/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Text improvement request schema.
 */
export type TextRequest = {
    /**
     * Text to improve
     */
    text: string;
    /**
     * AI text operation mode
     */
    mode: TextRequest.mode;
    /**
     * Custom instruction for 'custom' mode
     */
    custom_instruction?: (string | null);
    /**
     * LLM provider to use (optional, defaults to default provider)
     */
    provider?: (string | null);
    /**
     * LLM model to use (optional, defaults to first available)
     */
    model?: (string | null);
};
export namespace TextRequest {
    /**
     * AI text operation mode
     */
    export enum mode {
        CORRECT = 'correct',
        IMPROVE = 'improve',
        SUMMARIZE = 'summarize',
        EXPAND = 'expand',
        TRANSLATE_DE = 'translate_de',
        TRANSLATE_EN = 'translate_en',
        CUSTOM = 'custom',
    }
}

