# Template text that must never appear in the final deck

After building a deck, every text element must be user content, approved
boilerplate, or empty. Scan for these strings (case-insensitive). If any
remain, replace or clear them before handoff.

## Instructional labels (replace or clear)

- `Slide title should not exceed one line`
- `Slide title should not exceed three lines`
- `Presentation title should not exceed two lines`
- `Title should not exceed two lines`
- `Optional subheading`
- `Optional subheading should not exceed three lines`
- `Optional section marker`
- `Optional section marker here`
- `Optional supporting copy`
- `This section includes:`
- `What we'll discuss today`
- `Body headline`
- `Body cell should be limited to two lines`
- `Column header`
- `Row header`
- `Label`
- `Topic` (as repeated filler lines)
- `Details on topic`

## Placeholder copy

- `Lorem ipsum` (any fragment)
- `Insert source data here`
- `Source:\nInsert source data here`
- `Presenter's name`
- `Presenter's Name`
- `Template slide`
- `Click on this slide`
- `Quick tip`
- `Quick Tip`

## Placeholder numbers

- `00%` (template percentage placeholders)
- `000` (template number placeholders)
- `20XX` (template year placeholders)

## Boilerplate (OK only when intentionally kept)

The standard Red Hat closing paragraph is acceptable on the closing slide
ONLY if the deck spec explicitly includes it:

> Red Hat is the world's leading provider of enterprise open source
> software solutions. Award-winning support, training, and consulting
> services make Red Hat a trusted adviser to the Fortune 500.

## Verification procedure

1. Use `presentations get` to read all text from every slide
2. Search for each string above (case-insensitive substring match)
3. Zero hits required before the deck is considered complete
4. The `validate-slides.py` script automates this check
