import { Link } from 'react-router-dom';
import { commentsLabel, domainOf, timeAgo } from '../utils.js';
import VoteButtons from './VoteButtons.jsx';

export default function PostCard({ post, hideSnippet = false, children }) {
  return (
    <article className="card post-card">
      <VoteButtons kind="posts" id={post.id} score={post.score} myVote={post.my_vote} />
      <div className="post-main">
        <h2 className="post-title">
          {post.url ? (
            <a href={post.url} target="_blank" rel="noopener noreferrer nofollow">
              {post.title}
            </a>
          ) : (
            <Link to={`/post/${post.id}`}>{post.title}</Link>
          )}
          {post.url && <span className="domain">({domainOf(post.url)})</span>}
        </h2>
        {post.body && !hideSnippet && <p className="post-snippet">{post.body.length > 200 ? `${post.body.slice(0, 200)}…` : post.body}</p>}
        <div className="meta">
          {post.tag && (
            <Link to={`/?tag=${encodeURIComponent(post.tag)}`} className="tag">
              #{post.tag}
            </Link>
          )}
          <span>
            {post.author} · {timeAgo(post.created_at)}
          </span>
          <Link to={`/post/${post.id}`}>{commentsLabel(post.comment_count)}</Link>
          {children}
        </div>
      </div>
    </article>
  );
}
