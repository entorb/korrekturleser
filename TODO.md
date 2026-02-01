# TODO

## Vue

In the diff2html pnpm module, I use side-by-side config. How to add word wrap for long lines?

Add this CSS to your stylesheet:

```css
.d2h-code-line-ctn {
  white-space: pre-wrap !important;
  word-break: break-all;
}

.d2h-code-line {
  white-space: pre-wrap !important;
  word-break: break-all;
}
```

## Other

- try flask as V4
