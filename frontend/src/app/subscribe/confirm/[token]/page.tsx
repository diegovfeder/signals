"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

type ConfirmStatus = "loading" | "success" | "error";

interface ConfirmResponse {
  message: string;
  email: string;
}

interface ErrorResponse {
  detail: string;
}

export default function ConfirmEmailPage() {
  const params = useParams();
  const router = useRouter();
  const [status, setStatus] = useState<ConfirmStatus>("loading");
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    const confirmEmail = async () => {
      const token = params.token as string;

      if (!token) {
        setStatus("error");
        setMessage("Invalid confirmation link");
        return;
      }

      try {
        const apiUrl =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(
          `${apiUrl}/api/subscribe/confirm/${token}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          },
        );

        const data = await response.json();

        if (response.ok) {
          const confirmData = data as ConfirmResponse;
          setStatus("success");
          setMessage(confirmData.message);
          setEmail(confirmData.email);
          // Redirect to signals page after 3 seconds
          setTimeout(() => router.push("/signals"), 3000);
        } else {
          const errorData = data as ErrorResponse;
          setStatus("error");
          setMessage(errorData.detail || "Confirmation failed");
        }
      } catch (error) {
        setStatus("error");
        setMessage("Network error. Please try again.");
        console.error("[confirm] Error:", error);
      }
    };

    confirmEmail();
  }, [params.token, router]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        {status === "loading" && (
          <Card className="p-10 text-center border border-border animate-fade-in">
            <Loader2 className="h-16 w-16 text-ring mx-auto mb-6 animate-spin" />
            <h1 className="text-2xl font-bold text-foreground mb-3">
              Confirming your email...
            </h1>
            <p className="text-muted-foreground">Please wait a moment</p>
          </Card>
        )}

        {status === "success" && (
          <Card className="p-10 text-center border border-primary/30 animate-fade-in">
            <div className="mb-6 flex items-center justify-center">
              <div className="rounded-full bg-primary/20 p-4">
                <CheckCircle2 className="h-16 w-16 text-primary" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-4">
              Email confirmed!
            </h1>
            <p className="text-lg text-muted-foreground mb-4">{message}</p>
            {email && (
              <div className="mb-6 p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">
                  Confirmed email:
                </p>
                <p className="font-mono font-semibold text-foreground">
                  {email}
                </p>
              </div>
            )}
            <div className="mt-8 p-4 bg-primary/10 border border-primary/30 rounded-lg">
              <p className="text-sm text-ring flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Redirecting to dashboard in 3 seconds...
              </p>
            </div>
          </Card>
        )}

        {status === "error" && (
          <Card className="p-10 text-center border border-red-500/30 animate-fade-in">
            <div className="mb-6 flex items-center justify-center">
              <div className="rounded-full bg-red-500/20 p-4">
                <XCircle className="h-16 w-16 text-red-600" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-4">
              Confirmation failed
            </h1>
            <p className="text-lg text-muted-foreground mb-8">{message}</p>
            <Button
              onClick={() => router.push("/")}
              size="lg"
              className="w-full sm:w-auto"
            >
              Go back home
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}
