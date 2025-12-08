"""
Git utilities for analyzing repository changes.

Implements Step 1 from the paper: source code loading and commit analysis.
"""
import os
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import git
from git import Repo, Commit

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """
    Analyzes Git repositories to extract code changes for TD detection.
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize Git analyzer.
        
        Args:
            repo_path: Path to the Git repository
        """
        self.repo_path = Path(repo_path)
        
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        try:
            self.repo = Repo(repo_path)
        except git.InvalidGitRepositoryError:
            raise ValueError(f"Not a valid Git repository: {repo_path}")
        
        if self.repo.bare:
            raise ValueError(f"Cannot analyze bare repository: {repo_path}")
    
    def get_recent_commits(
        self, 
        max_count: int = 10,
        branch: Optional[str] = None
    ) -> List[Commit]:
        """
        Get recent commits from the repository.
        
        Args:
            max_count: Maximum number of commits to retrieve
            branch: Optional branch name (default: current branch)
            
        Returns:
            List of Commit objects
        """
        try:
            if branch:
                commits = list(self.repo.iter_commits(branch, max_count=max_count))
            else:
                commits = list(self.repo.iter_commits(max_count=max_count))
            
            logger.info(f"Retrieved {len(commits)} commits")
            return commits
            
        except Exception as e:
            logger.error(f"Error retrieving commits: {e}")
            return []
    
    def get_commit_diff(
        self, 
        commit: Commit,
        context_lines: int = 3
    ) -> Dict[str, str]:
        """
        Get the diff for a specific commit.
        
        Args:
            commit: The commit to analyze
            context_lines: Number of context lines around changes
            
        Returns:
            Dictionary mapping file paths to their diffs
        """
        file_diffs = {}
        
        try:
            # Get parent commit for comparison
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit, create_patch=True)
            else:
                # First commit - compare with empty tree
                diffs = commit.diff(git.NULL_TREE, create_patch=True)
            
            for diff in diffs:
                if diff.a_path:
                    file_path = diff.a_path
                elif diff.b_path:
                    file_path = diff.b_path
                else:
                    continue
                
                # Get the actual diff text
                if diff.diff:
                    file_diffs[file_path] = diff.diff.decode('utf-8', errors='replace')
            
            logger.info(f"Extracted diffs for {len(file_diffs)} files from commit {commit.hexsha[:8]}")
            return file_diffs
            
        except Exception as e:
            logger.error(f"Error getting commit diff: {e}")
            return {}
    
    def get_modified_files(
        self,
        commit: Commit
    ) -> List[str]:
        """
        Get list of modified files in a commit.
        
        Args:
            commit: The commit to analyze
            
        Returns:
            List of file paths
        """
        try:
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit)
            else:
                diffs = commit.diff(git.NULL_TREE)
            
            files = []
            for diff in diffs:
                if diff.a_path:
                    files.append(diff.a_path)
                elif diff.b_path:
                    files.append(diff.b_path)
            
            return files
            
        except Exception as e:
            logger.error(f"Error getting modified files: {e}")
            return []
    
    def get_file_content_at_commit(
        self,
        commit: Commit,
        file_path: str
    ) -> Optional[str]:
        """
        Get the content of a file at a specific commit.
        
        Args:
            commit: The commit
            file_path: Path to the file
            
        Returns:
            File content as string, or None if not found
        """
        try:
            # Try to get the file from the commit's tree
            blob = commit.tree / file_path
            content = blob.data_stream.read()
            return content.decode('utf-8', errors='replace')
            
        except (KeyError, AttributeError) as e:
            logger.warning(f"File {file_path} not found in commit {commit.hexsha[:8]}")
            return None
        except Exception as e:
            logger.error(f"Error reading file content: {e}")
            return None
    
    def get_uncommitted_changes(self) -> Dict[str, str]:
        """
        Get uncommitted changes in the working directory.
        
        Returns:
            Dictionary mapping file paths to their diffs
        """
        file_diffs = {}
        
        try:
            # Get diffs for tracked files with changes
            diffs = self.repo.index.diff(None, create_patch=True)
            
            for diff in diffs:
                if diff.a_path:
                    file_path = diff.a_path
                    if diff.diff:
                        file_diffs[file_path] = diff.diff.decode('utf-8', errors='replace')
            
            # Also check for untracked files
            untracked = self.repo.untracked_files
            for file_path in untracked:
                try:
                    full_path = self.repo_path / file_path
                    if full_path.exists() and full_path.is_file():
                        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            # Create a "diff" for new files
                            file_diffs[file_path] = f"+++ {file_path}\n{content}"
                except Exception as e:
                    logger.warning(f"Could not read untracked file {file_path}: {e}")
            
            logger.info(f"Found {len(file_diffs)} files with uncommitted changes")
            return file_diffs
            
        except Exception as e:
            logger.error(f"Error getting uncommitted changes: {e}")
            return {}
    
    def get_line_numbers_from_diff(self, diff_text: str) -> List[Tuple[int, int]]:
        """
        Extract line number ranges from a diff.
        
        Args:
            diff_text: The diff text
            
        Returns:
            List of (start_line, end_line) tuples
        """
        line_ranges = []
        current_line = 0
        
        for line in diff_text.split('\n'):
            if line.startswith('@@'):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                try:
                    parts = line.split('@@')[1].strip().split()
                    if len(parts) >= 2:
                        new_info = parts[1]  # +new_start,new_count
                        if ',' in new_info:
                            start, count = new_info[1:].split(',')
                            start = int(start)
                            count = int(count)
                            if count > 0:
                                line_ranges.append((start, start + count - 1))
                                current_line = start
                        else:
                            # Single line change
                            start = int(new_info[1:])
                            line_ranges.append((start, start))
                            current_line = start
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse hunk header: {line}")
                    continue
            elif line.startswith('+') and not line.startswith('+++'):
                # Track added lines
                current_line += 1
            elif not line.startswith('-'):
                # Context or unchanged lines
                current_line += 1
        
        return line_ranges
    
    def is_code_file(self, file_path: str) -> bool:
        """
        Check if a file is a code file (not binary, config, etc.).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if it's a code file
        """
        code_extensions = {
            '.py', '.java', '.js', '.ts', '.jsx', '.tsx',
            '.c', '.cpp', '.h', '.hpp', '.cs', '.go',
            '.rb', '.php', '.scala', '.kt', '.swift',
            '.rs', '.r', '.m', '.sh', '.sql'
        }
        
        path = Path(file_path)
        return path.suffix.lower() in code_extensions
