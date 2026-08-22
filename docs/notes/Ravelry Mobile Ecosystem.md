---
aliases:
  - "Mobile Ecosystem"
tags:
  - ravelry
  - documentation
---

# Ravelry Mobile Ecosystem

**The Mobile Ecosystem is perhaps the most visible manifestation of the Ravelry API in action.** Because Ravelry operates with an incredibly small core team—historically consisting of only four people with a single programmer—the platform made the strategic decision early on *not* to develop or maintain official native applications for iOS, Android, or Windows Phone. 

Instead, the company focused its resources on two primary objectives: maintaining a mobile-optimized website (`m.ravelry.com`) for small touch screens, and building a robust REST API to completely outsource mobile app development to third-party developers within the community. 

Here is a detailed overview of how the mobile ecosystem is structured and the applications that drive it:

### 1. Architectural Constraints: Security and Tooling
Developing for the mobile ecosystem requires navigating strict architectural boundaries. Because native mobile applications are distributed public clients, they are strictly prohibited from using Basic HTTP Authentication, which would expose user credentials.
*   **OAuth 2.0 Mandate:** Mobile apps must utilize dynamic, three-legged OAuth 2.0 so users can securely log into their own Ravelry accounts. 
*   **App Schemes and Callbacks:** Ravelry explicitly does not support "Out-of-Band" (OOB) authorization. This means mobile developers must engineer strict internal app schemes or dedicated callback URLs to automatically catch token redirects from the browser back to the app. 
*   **Development SDKs:** To manage these complex network interactions, the developer community has built language-specific tools. Android developers heavily utilize **`retroravelry`**, an open-source Kotlin wrapper built on Retrofit and Coroutines to handle asynchronous background API requests. Similarly, iOS developers rely on libraries like **OAuthSwift** to successfully navigate Ravelry's strict authentication gateways.

### 2. The Apple iOS Ecosystem
The API has enabled developers to build dedicated tools specifically optimized for iPhones and iPads, filling functionality gaps that a standard web browser cannot cover.
*   **Wooly:** Created by developers `MenKnitToo` and `dstys`, Wooly was the very first iOS app designed to provide on-the-go access to a user's Ravelry "Notebook." It allowed iPhone users to edit project details, access their stash and queue, view friends' projects, and featured a built-in photo editor to enhance images before pushing them to the Ravelry database.
*   **Yarma:** An iOS camera app designed for iPhone and iPad that allowed users to take pictures of their latest Work-In-Progress (WIP) or new yarn, apply custom filters, and upload the image directly to the relevant Ravelry project or stash entry.
*   **GoodReader Integration:** The API extends beyond dedicated crafting apps into general utility apps. iPad and iPhone users can connect the popular PDF viewing app, GoodReader, directly to their Ravelry API library token, allowing them to natively load and view purchased pattern PDFs without needing to manually copy or sync the files.

### 3. The Android Ecosystem
Android developers have utilized the API to build highly specialized utility apps that enhance the physical crafting experience.
*   **Ravulous:** A highly popular Android app for phones and tablets that leveraged the API to provide push notifications for new Ravelry private messages and unread forum replies. It was heavily used as a shopping companion, allowing crafters to look up their queued projects to check required yardages while standing in a physical yarn store.
*   **Ravelry Photo Uploader:** Because the main Ravelry website traditionally required users to upload photos via a computer interface, developers built this app to bypass the browser entirely. It allowed users to select photos from their Android gallery or take new ones and "Share" them directly into the API to attach to a stash or project.
*   **County Plus:** A digital row-counter application that integrated with the API to automatically import a user's current project names directly from Ravelry, allowing them to keep track of their progress and edit their project notes natively on the device.

### 4. Windows Phone and Cross-Platform Tools
While iOS and Android dominate, the API's platform-agnostic design allowed developers to serve niche mobile markets as well.
*   **Stitch:** An open-source application built specifically for the Windows Phone 7 interface, allowing those users to view free patterns, check their queues, and upload photos with a slick, native Windows Phone UI.
*   **KnitKapp:** A cross-platform mobile utility designed to help crafters manage their physical inventories (needles, hooks, yarn). While the app could function offline without a Ravelry account, users who plugged in their API credentials unlocked advanced, synchronized Ravelry features on the go.
