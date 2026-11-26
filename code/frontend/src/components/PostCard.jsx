import { Link } from 'react-router-dom';
import { commentsLabel, domainOf, timeAgo } from '../utils.js';
import Avatar from './Avatar.jsx';
import { Clock, CommentIcon, LinkIcon } from './Icon.jsx';
import VoteButtons from './VoteButtons.jsx';

export default function PostCard({ post, hideSnippet = false, children }) {
  return (
    <article className="card post-card">
      <VoteButtons kind="posts" id={post.id} score={post.score} myVote={post.my_vote} />
      <div className="post-main">
        <div className="post-head">
          {post.tag && (
            <Link to={`/?tag=${encodeURIComponent(post.tag)}`} className="tag">
              #{post.tag}
            </Link>
          )}
          {post.url && (
            <span className="domain">
              <LinkIcon />
              {domainOf(post.url)}
            </span>
          )}
        </div>
        <h2 className="post-title">
          {post.url ? (
            <a href={post.url} target="_blank" rel="noopener noreferrer nofollow">
              {post.title}
            </a>
          ) : (
            <Link to={`/post/${post.id}`}>{post.title}</Link>
          )}
        </h2>
        {post.body && !hideSnippet && <p className="post-snippet">{post.body}</p>}
        <div className="meta">
          <span className="author">
            <Avatar name={post.author} />
            {post.author}
          </span>
          <span className="meta-item">
            <Clock />
            {timeAgo(post.created_at)}
          </span>
          <Link to={`/post/${post.id}`}>
            <CommentIcon />
            {commentsLabel(post.comment_count)}
          </Link>
          {children && <span className="meta-actions">{children}</span>}
        </div>
      </div>
    </article>
  );
}
