class ProgressTracker:
    def get_progress(self, context):
        try:
            progress = context.get("progress", [])

            if not progress:
                return {
                    "message": "No progress data available yet."
                }

            return {
                "progress": progress
            }

        except Exception as e:
            print("❌ PROGRESS TRACKER ERROR:", str(e))
            return {
                "error": "Failed to fetch progress data"
            }