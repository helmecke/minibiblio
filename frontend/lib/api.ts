const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type LoginPayload = {
  username: string;
  password: string;
};

export async function authenticate(endpoint: "/auth/login" | "/auth/admin/login", payload: LoginPayload) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "content-type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Unable to authenticate");
  }

  return response.json();
}
