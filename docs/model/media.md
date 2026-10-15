# Media

## Description

`Media` is one multimedia item of the offer — a photo, a video, a floor
plan or a virtual tour — referenced by URL. The optional `position` defines
the display order.

The caption is a **language map**, like every other text meant for people
in the format. A portal that presents an offer in several languages can
then show the caption in the same language as the rest of the advert,
instead of falling back to the language of the producer.

The entity is typed as `schema:MediaObject` or one of its subtypes (for
example `ImageObject`, `VideoObject`) and as `erdif:Media`.

## Properties

--8<-- "_partials/terms-media.md"

## Validation rules

--8<-- "_partials/rules-media.md"

## Example

```json
"media": [
  {
    "@type": ["ImageObject", "erdif:Media"],
    "mediaType": "InsidePhoto",
    "contentUrl": "https://cdn.example.com/adverts/009874/01.jpg",
    "position": 1,
    "caption": {
      "cs": "Obývací pokoj s kuchyňským koutem",
      "en": "Living room with a kitchenette"
    }
  }
]
```
