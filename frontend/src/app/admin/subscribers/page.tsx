"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useSubscribers } from "@/lib/hooks/useSignals";
import Link from "next/link";

export default function AdminSubscribersPage() {
  const [includeUnsubscribed, setIncludeUnsubscribed] = useState(true);
  const [includeTokens, setIncludeTokens] = useState(false);

  const { data, isLoading, isError, error, refetch, isFetching } =
    useSubscribers({
      includeUnsubscribed,
      includeTokens,
      limit: 200,
    });

  const subscribers = data?.subscribers ?? [];

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between flex-wrap gap-4 mb-2">
        <div className="flex items-center flex-wrap gap-4">
          <Button asChild variant="secondary" size="sm">
            <Link href="/admin">← Back</Link>
          </Button>
          <h1 className="text-3xl font-bold text-foreground">Subscribers</h1>
          <p className="text-sm text-muted-foreground">
            Inspect the email list captured via the landing page and dashboard
            forms. Use tokens for manual unsubscribe/testing only.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => refetch()}
            variant="secondary"
            size="sm"
            disabled={isFetching}
            loading={isFetching}
          >
            Refresh data
          </Button>
        </div>
      </header>

      <Card className="p-6 space-y-4 border border-border">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <label className="flex items-center gap-2 text-foreground cursor-pointer">
            <input
              type="checkbox"
              className="accent-primary"
              checked={includeUnsubscribed}
              onChange={(event) => setIncludeUnsubscribed(event.target.checked)}
            />
            Show unsubscribed
          </label>
          <label className="flex items-center gap-2 text-foreground cursor-pointer">
            <input
              type="checkbox"
              className="accent-primary"
              checked={includeTokens}
              onChange={(event) => setIncludeTokens(event.target.checked)}
            />
            Include tokens
          </label>
          <span className="text-muted-foreground text-xs">
            Total in DB: {data?.total ?? 0} · showing {subscribers.length}
          </span>
        </div>

        {isLoading && (
          <p className="text-sm text-muted-foreground">Loading subscribers…</p>
        )}
        {isError && (
          <p className="text-sm text-red-600">
            Failed to load subscribers:&nbsp;
            {String((error as Error)?.message ?? error)}
          </p>
        )}

        {!isLoading && !isError && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-muted-foreground border-b border-border">
                  <th className="py-2 pr-4">Email</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Subscribed</th>
                  <th className="py-2 pr-4">Confirmed</th>
                  {includeTokens && (
                    <>
                      <th className="py-2 pr-4">Confirmation token</th>
                      <th className="py-2 pr-4">Unsubscribe token</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {subscribers.map((subscriber, idx) => (
                  <tr
                    key={`${subscriber.email}-${idx}`}
                    className="border-b border-border/40"
                  >
                    <td className="py-2 pr-4 font-mono text-foreground">
                      {subscriber.email}
                    </td>
                    <td className="py-2 pr-4">
                      {subscriber.unsubscribed ? (
                        <Badge className="bg-yellow-500/20 text-yellow-500 border-0">
                          Unsubscribed
                        </Badge>
                      ) : (
                        <Badge className="bg-primary/20 text-ring border-0">
                          Active
                        </Badge>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-muted-foreground">
                      {subscriber.subscribed_at
                        ? new Date(subscriber.subscribed_at).toLocaleString()
                        : "—"}
                    </td>
                    <td className="py-2 pr-4 text-muted-foreground">
                      {subscriber.confirmed_at
                        ? new Date(subscriber.confirmed_at).toLocaleString()
                        : subscriber.confirmed
                          ? "Pending timestamp"
                          : "Not confirmed"}
                    </td>
                    {includeTokens && (
                      <>
                        <td className="py-2 pr-4 font-mono text-xs text-muted-foreground">
                          {subscriber.confirmation_token ?? "—"}
                        </td>
                        <td className="py-2 pr-4 font-mono text-xs text-muted-foreground">
                          {subscriber.unsubscribe_token ?? "—"}
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
