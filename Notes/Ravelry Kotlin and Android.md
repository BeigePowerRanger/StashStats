---
aliases:
  - "Kotlin & Android"
tags:
  - ravelry
  - documentation
---

# Ravelry Kotlin and Android

**Android and Kotlin development play a critical role in the Ravelry API ecosystem because Ravelry does not build or maintain its own official native mobile applications**. Operating with a very small core team—historically including only one programmer—Ravelry explicitly chose to focus its internal resources on improving its mobile-optimized website and expanding its REST API. Consequently, the platform relies entirely on third-party developers to bring Ravelry's massive database to Android devices. 

To support this mobile developer community, specialized open-source tools, Kotlin libraries, and dedicated applications have emerged within the ecosystem.

### 1. The `retroravelry` Kotlin Wrapper
Because mobile applications must efficiently manage network calls without freezing the user interface, Android developers require robust, asynchronous networking libraries. To solve this within the Ravelry ecosystem, the community built **`retroravelry`**, an open-source wrapper specifically designed for the Ravelry API and written in Kotlin. 

*   **Architecture:** The library is built on top of **Retrofit** (a popular type-safe HTTP client for Android) and utilizes **Kotlin Coroutines** to seamlessly manage background API requests. 
*   **Testing and Integration:** The `retroravelry` repository provides a highly useful developer tool: a dedicated Postman collection (`ravelry_postman_collection.json`). Android developers can import this file into the Postman application to visually browse the REST API endpoints, inspect deeply nested JSON payloads, and generate mock OAuth 2.0 access tokens to test their code before deploying it to production.

### 2. Mobile Authentication Constraints (OAuth 2.0)
Within the larger context of Ravelry's security architecture, Android apps built with Kotlin are strictly prohibited from using Basic HTTP Authentication. 
*   Because an Android app is a distributed public client, **dynamic three-legged OAuth 2.0 is required** to ensure that end-users can securely log into their own Ravelry accounts without exposing their private credentials to the application developer.
*   When implementing these flows in Kotlin, developers must adhere to Ravelry's strict security validators. Crucially, the OAuth `state` parameter must be a secure, random string that is **strictly greater than eight characters in length**. Furthermore, "Out-of-Band" (OOB) authorization is not supported, so Android apps must utilize strict callback URLs or internal app schemes to catch token redirects.

### 3. Real-World Android Applications
Historically, third-party developers have successfully leveraged the API to build Android tools that enhance the crafting experience on the go:
*   **Ravulous:** This was a popular Android application designed for smartphones and tablets that used the Ravelry API to offer "knitterly things on-the-go". It provided push notifications for new Ravelry private messages and unread forum replies. It also allowed users to search the pattern database and look up their queued projects to check recommended yarn yardages while physically shopping at a yarn store.
*   **Ravelry Photo Uploader:** Because the Ravelry website traditionally required users to upload photos from a computer, developers built this dedicated Android app. It allowed users to bypass the browser, take a photo with their Android phone's camera or gallery, and share it directly to Ravelry to attach to a specific project or stashed yarn.
*   **County Plus:** An Android row counter application that integrated with the API to import a user's current Work-In-Progress (WIP) names directly from Ravelry, while also allowing the crafter to edit their project notes natively on their device.
