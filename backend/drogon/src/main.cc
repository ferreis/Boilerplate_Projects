#include <drogon/drogon.h>

#include <cstdlib>
#include <functional>
#include <string>

namespace {
int backendPort() {
    const char *configuredPort = std::getenv("BACKEND_PORT");
    if (configuredPort == nullptr || std::string(configuredPort).empty()) {
        return 8000;
    }

    return std::stoi(configuredPort);
}
}  // namespace

int main() {
    auto &application = drogon::app();

    application.registerHandler(
        "/health",
        [](const drogon::HttpRequestPtr &,
           std::function<void(const drogon::HttpResponsePtr &)> &&callback) {
            Json::Value body;
            body["status"] = "ok";
            callback(drogon::HttpResponse::newHttpJsonResponse(body));
        },
        {drogon::Get});

    application.addListener("0.0.0.0", backendPort());
    application.run();
}
