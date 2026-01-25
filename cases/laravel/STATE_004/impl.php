<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Article;
use App\Models\ArticleReview;
use App\Models\User;

class ArticleWorkflowService
{
    public function submitForReview(int $articleId, User $author): array
    {
        $article = Article::findOrFail($articleId);

        if ($article->author_id !== $author->id) {
            return [
                'success' => false,
                'message' => 'Only the author can submit for review',
            ];
        }

        if ($article->status !== 'draft') {
            return [
                'success' => false,
                'message' => 'Only drafts can be submitted for review',
            ];
        }

        $article->update(['status' => 'pending_review']);

        return ['success' => true, 'article' => $article];
    }

    public function review(int $articleId, User $reviewer, string $decision, ?string $comments): array
    {
        $article = Article::findOrFail($articleId);

        if ($article->status !== 'pending_review') {
            return [
                'success' => false,
                'message' => 'Article is not pending review',
            ];
        }

        ArticleReview::create([
            'article_id' => $articleId,
            'reviewer_id' => $reviewer->id,
            'decision' => $decision,
            'comments' => $comments,
        ]);

        $newStatus = $decision === 'approved' ? 'approved' : 'draft';
        $article->update(['status' => $newStatus]);

        return ['success' => true, 'article' => $article];
    }

    public function publish(int $articleId, User $editor): array
    {
        $article = Article::findOrFail($articleId);

        // BUG: Allows publishing from 'pending_review' status, skipping approval
        // Should only allow publishing from 'approved' or 'unpublished'
        if (!in_array($article->status, ['approved', 'unpublished', 'pending_review'])) {
            return [
                'success' => false,
                'message' => 'Article cannot be published in current state',
            ];
        }

        $article->update([
            'status' => 'published',
            'published_at' => $article->published_at ?? now(),
        ]);

        return ['success' => true, 'article' => $article];
    }

    public function unpublish(int $articleId): array
    {
        $article = Article::findOrFail($articleId);

        if ($article->status !== 'published') {
            return [
                'success' => false,
                'message' => 'Only published articles can be unpublished',
            ];
        }

        $article->update(['status' => 'unpublished']);

        return ['success' => true, 'article' => $article];
    }

    public function archive(int $articleId): array
    {
        $article = Article::findOrFail($articleId);

        if ($article->status !== 'published') {
            return [
                'success' => false,
                'message' => 'Only published articles can be archived',
            ];
        }

        $article->update(['status' => 'archived']);

        return ['success' => true, 'article' => $article];
    }
}
