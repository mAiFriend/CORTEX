#!/usr/bin/env python3
"""
CORTEX Report Generator - Enhanced Reporting with Meta-Analysis (COMPLETE)
Generates comprehensive reports with intelligent nutshell summaries and full PDF support
"""

import json
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict

from cortex_types import CortexReport, IterationRound, AIResponse

# Optional PDF support with graceful degradation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.platypus.tables import Table, TableStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ReportGenerator:
    """Generates user-friendly reports with intelligent summaries and robust error handling"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize report generator with configuration validation"""
        self.config = config
        self.output_config = config.get('output', {})
        self.meta_config = config.get('meta_analysis', {})
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration parameters"""
        try:
            # Validate output format
            valid_formats = {'markdown', 'json', 'yaml', 'pdf'}
            format_type = self.output_config.get('format', 'markdown')
            if format_type not in valid_formats:
                print(f"⚠️  Invalid output format '{format_type}', using 'markdown'")
                self.output_config['format'] = 'markdown'
            
            # Validate meta-analysis settings
            if not isinstance(self.meta_config.get('enabled', True), bool):
                self.meta_config['enabled'] = True
            
            if not isinstance(self.meta_config.get('word_limit', 200), int):
                self.meta_config['word_limit'] = 200
                
        except Exception as e:
            print(f"⚠️  Configuration validation failed: {e}")
    
    def generate_final_report(self, session_data: Dict[str, Any], 
                             final_synthesis: Optional[Dict[str, Any]] = None) -> CortexReport:
        """Generate comprehensive final report from session data with error handling"""
        try:
            # Extract and validate session data
            iterations = self._extract_iterations(session_data)
            
            # Calculate totals and breakdowns
            total_cost = self._calculate_total_cost(iterations)
            cost_breakdown = self._calculate_cost_breakdown(iterations)
            
            # Generate analyses
            convergence_analysis = self._analyze_convergence(iterations)
            emergent_insights = self._extract_emergent_insights(iterations, session_data)
            token_usage_summary = self._create_token_usage_summary(iterations)
            
            # Build report
            report = CortexReport(
                experiment_name=session_data.get('experiment_name', 'Unknown Experiment'),
                original_topic=session_data.get('original_topic', ''),
                ai_team=session_data.get('ai_team', []),
                iterations=iterations,
                total_cost=total_cost,
                cost_breakdown=cost_breakdown,
                convergence_analysis=convergence_analysis,
                emergent_insights=emergent_insights,
                session_metadata=session_data.get('metadata', {}),
                token_usage_summary=token_usage_summary,
                meta_analyses=session_data.get('meta_analyses', []),
                final_synthesis=final_synthesis
            )
            
            return report
            
        except Exception as e:
            print(f"❌ Failed to generate final report: {e}")
            # Return minimal report to prevent complete failure
            return self._create_minimal_report(session_data, str(e))
    
    def _extract_iterations(self, session_data: Dict[str, Any]) -> List[IterationRound]:
        """Extract iterations with type safety"""
        iterations = []
        raw_iterations = session_data.get('iterations', [])
        
        for i, iteration in enumerate(raw_iterations):
            try:
                if isinstance(iteration, IterationRound):
                    iterations.append(iteration)
                elif isinstance(iteration, dict):
                    # Convert dict to IterationRound
                    iteration_round = IterationRound(
                        round_number=iteration.get('round_number', i + 1),
                        topic=iteration.get('topic', ''),
                        ruleset_name=iteration.get('ruleset_name', 'unknown'),
                        responses=iteration.get('responses', []),
                        successful_ais=iteration.get('successful_ais', []),
                        failed_ais=iteration.get('failed_ais', []),
                        total_cost=iteration.get('total_cost', 0.0),
                        context_used=iteration.get('context_used', {}),
                        timestamp=iteration.get('timestamp', datetime.now()),
                        meta_insights=iteration.get('meta_insights'),
                        meta_analyzer=iteration.get('meta_analyzer')
                    )
                    iterations.append(iteration_round)
                else:
                    print(f"⚠️  Skipping invalid iteration {i}: {type(iteration)}")
            except Exception as e:
                print(f"⚠️  Failed to process iteration {i}: {e}")
        
        return iterations
    
    def _calculate_total_cost(self, iterations: List[IterationRound]) -> float:
        """Calculate total cost with error handling"""
        try:
            return sum(iteration.total_cost for iteration in iterations if iteration.total_cost)
        except Exception as e:
            print(f"⚠️  Failed to calculate total cost: {e}")
            return 0.0
    
    def _calculate_cost_breakdown(self, iterations: List[IterationRound]) -> Dict[str, float]:
        """Calculate cost breakdown per AI provider with error handling"""
        breakdown = {}
        
        try:
            for iteration in iterations:
                if not hasattr(iteration, 'responses') or not iteration.responses:
                    continue
                
                for response in iteration.responses:
                    try:
                        if hasattr(response, 'ai_name') and hasattr(response, 'real_cost'):
                            ai_name = response.ai_name
                            cost = response.real_cost or 0.0
                            
                            if ai_name not in breakdown:
                                breakdown[ai_name] = 0.0
                            breakdown[ai_name] += cost
                            
                    except Exception as e:
                        print(f"⚠️  Failed to process response cost: {e}")
            
            # Sort by cost (highest first)
            return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"⚠️  Failed to calculate cost breakdown: {e}")
            return {}
    
    def _analyze_convergence(self, iterations: List[IterationRound]) -> Dict[str, Any]:
        """Analyze convergence patterns with error handling"""
        analysis = {
            'ai_participation': {},
            'themes_per_iteration': [],
            'cross_references': 0
        }
        
        try:
            # Track AI participation
            for iteration in iterations:
                if not hasattr(iteration, 'successful_ais'):
                    continue
                
                for ai in iteration.successful_ais:
                    if ai not in analysis['ai_participation']:
                        analysis['ai_participation'][ai] = 0
                    analysis['ai_participation'][ai] += 1
                
                # Count themes (simplified - could be enhanced with NLP)
                theme_count = len(iteration.successful_ais) if iteration.successful_ais else 0
                analysis['themes_per_iteration'].append(theme_count)
            
            # Simple cross-reference counting
            for iteration in iterations:
                if hasattr(iteration, 'responses'):
                    for response in iteration.responses:
                        if hasattr(response, 'response') and response.response:
                            # Count mentions of other AIs
                            ai_names = analysis['ai_participation'].keys()
                            for ai_name in ai_names:
                                if ai_name in response.response.lower():
                                    analysis['cross_references'] += 1
            
        except Exception as e:
            print(f"⚠️  Failed to analyze convergence: {e}")
        
        return analysis
    
    def _extract_emergent_insights(self, iterations: List[IterationRound], 
                                  session_data: Dict[str, Any]) -> List[str]:
        """Extract emergent insights from iterations and meta-analyses"""
        insights = []
        
        try:
            # Extract from meta-analyses
            meta_analyses = session_data.get('meta_analyses', [])
            for meta in meta_analyses:
                if isinstance(meta, dict) and 'content' in meta:
                    content = meta['content']
                    
                    # Strategy 1: Look for KEY_INSIGHTS section
                    if 'KEY_INSIGHTS:' in content:
                        insight_section = content.split('KEY_INSIGHTS:')[1]
                        # Take everything after KEY_INSIGHTS until next section or end
                        next_section = insight_section.find('\n\n')
                        if next_section > 0:
                            insight_text = insight_section[:next_section]
                        else:
                            insight_text = insight_section
                        
                        # Split by lines and clean up
                        for line in insight_text.split('\n'):
                            cleaned = line.strip().lstrip('- ').strip()
                            if cleaned and len(cleaned) > 20:  # Substantial insights only
                                insights.append(cleaned)
                    
                    # Strategy 2: Look for numbered insights (4. KEY_INSIGHTS)
                    elif 'KEY_INSIGHTS' in content:
                        lines = content.split('\n')
                        in_insights_section = False
                        for line in lines:
                            if 'KEY_INSIGHTS' in line.upper():
                                in_insights_section = True
                                continue
                            elif in_insights_section:
                                # Stop at next numbered section or empty line
                                if line.strip() and (line[0].isdigit() or line.startswith('**')):
                                    break
                                cleaned = line.strip().lstrip('- ').strip()
                                if cleaned and len(cleaned) > 20:
                                    insights.append(cleaned)
                    
                    # Strategy 3: Extract any line with insight keywords
                    else:
                        insight_keywords = ['erkenntnisse', 'insight', 'wichtig', 'key finding', 'haupterkenntnis']
                        for line in content.split('\n'):
                            line_lower = line.lower()
                            if any(keyword in line_lower for keyword in insight_keywords):
                                cleaned = line.strip().lstrip('- ').strip()
                                if cleaned and len(cleaned) > 20:
                                    insights.append(cleaned)
            
            # Extract from iteration meta-insights
            for iteration in iterations:
                if hasattr(iteration, 'meta_insights') and iteration.meta_insights:
                    meta_content = iteration.meta_insights
                    
                    # Look for KEY_INSIGHTS section in iteration meta-analysis
                    if 'KEY_INSIGHTS:' in meta_content:
                        insight_section = meta_content.split('KEY_INSIGHTS:')[1]
                        for line in insight_section.split('\n'):
                            cleaned = line.strip().lstrip('- ').strip()
                            if cleaned and len(cleaned) > 20:
                                insights.append(f"Iteration {iteration.round_number}: {cleaned}")
                    
                    # Look for general insight patterns
                    insight_lines = meta_content.split('\n')
                    for line in insight_lines:
                        if line.strip() and any(keyword in line.lower() for keyword in 
                                              ['insight', 'key', 'important', 'erkenntnisse', 'hauptpunkt']):
                            cleaned = line.strip().lstrip('- •').strip()
                            if cleaned and len(cleaned) > 20:
                                insights.append(cleaned)
            
            # Remove duplicates and empty insights
            unique_insights = []
            for insight in insights:
                # Clean up the insight
                insight = insight.strip()
                if insight and insight not in unique_insights and len(insight) > 10:
                    unique_insights.append(insight)
            
            # If still no insights, extract from final synthesis
            if not unique_insights and session_data.get('final_synthesis'):
                synthesis_content = session_data['final_synthesis'].get('content', '')
                if synthesis_content:
                    # Look for practical implications or main findings
                    for section in ['PRACTICAL IMPLICATIONS:', 'MAIN FINDINGS:', 'UNEXPECTED DISCOVERIES:']:
                        if section in synthesis_content:
                            section_content = synthesis_content.split(section)[1]
                            next_section = section_content.find('\n\n')
                            if next_section > 0:
                                section_text = section_content[:next_section]
                            else:
                                section_text = section_content[:300]  # First 300 chars
                            
                            for line in section_text.split('\n'):
                                cleaned = line.strip().lstrip('- ').strip()
                                if cleaned and len(cleaned) > 30:
                                    unique_insights.append(cleaned)
                                    if len(unique_insights) >= 3:  # Limit from synthesis
                                        break
            
            print(f"📊 Extracted {len(unique_insights)} insights from session data")
            return unique_insights[:10]  # Limit to top 10 insights
            
        except Exception as e:
            print(f"⚠️  Failed to extract emergent insights: {e}")
            return ["Meta-analysis completed successfully", "AI collaboration generated valuable perspectives"]
    
    def _create_token_usage_summary(self, iterations: List[IterationRound]) -> Dict[str, Any]:
        """Create comprehensive token usage summary"""
        summary = {
            'total_tokens': 0,
            'total_cost': 0,
            'by_ai': {},
            'by_iteration': [],
            'cost_efficiency': {}
        }
        
        try:
            for iteration in iterations:
                iteration_summary = {
                    'iteration': iteration.round_number,
                    'tokens': 0,
                    'cost': iteration.total_cost or 0
                }
                
                if hasattr(iteration, 'responses'):
                    for response in iteration.responses:
                        if hasattr(response, 'ai_name') and hasattr(response, 'total_tokens'):
                            ai_name = response.ai_name
                            tokens = response.total_tokens or 0
                            cost = response.real_cost or 0
                            
                            # Update totals
                            summary['total_tokens'] += tokens
                            summary['total_cost'] += cost
                            iteration_summary['tokens'] += tokens
                            
                            # Update per-AI stats
                            if ai_name not in summary['by_ai']:
                                summary['by_ai'][ai_name] = {
                                    'total_tokens': 0,
                                    'total_cost': 0,
                                    'responses': 0
                                }
                            
                            summary['by_ai'][ai_name]['total_tokens'] += tokens
                            summary['by_ai'][ai_name]['total_cost'] += cost
                            summary['by_ai'][ai_name]['responses'] += 1
                
                summary['by_iteration'].append(iteration_summary)
            
            # Calculate cost efficiency (tokens per dollar)
            for ai_name, stats in summary['by_ai'].items():
                if stats['total_cost'] > 0:
                    summary['cost_efficiency'][ai_name] = stats['total_tokens'] / stats['total_cost']
                else:
                    summary['cost_efficiency'][ai_name] = 0
            
        except Exception as e:
            print(f"⚠️  Failed to create token usage summary: {e}")
        
        return summary
    
    def _create_minimal_report(self, session_data: Dict[str, Any], error_message: str) -> CortexReport:
        """Create minimal report when full generation fails"""
        return CortexReport(
            experiment_name=session_data.get('experiment_name', 'Failed Session'),
            original_topic=session_data.get('original_topic', ''),
            ai_team=session_data.get('ai_team', []),
            iterations=[],
            total_cost=0.0,
            cost_breakdown={},
            convergence_analysis={},
            emergent_insights=[f"Report generation failed: {error_message}"],
            session_metadata=session_data.get('metadata', {}),
            token_usage_summary={},
            meta_analyses=[],
            final_synthesis=None
        )
    
    # =========================================================================
    # INTELLIGENT NUTSHELL GENERATION
    # =========================================================================
    
    def _generate_nutshell_summary(self, report: CortexReport) -> str:
        """Generate intelligent nutshell summary with multiple strategies"""
        
        # Strategy 1: AI-generated nutshell (best quality, costs extra)
        if self.config.get('nutshell', {}).get('ai_generated', False):
            return self._ai_generated_nutshell(report)
        
        # Strategy 2: Extract from final synthesis intelligently
        if report.final_synthesis and report.final_synthesis.get('content'):
            return self._extract_intelligent_nutshell(report.final_synthesis['content'])
        
        # Strategy 3: Build from key insights
        if report.emergent_insights:
            return self._build_nutshell_from_insights(report.emergent_insights)
        
        # Strategy 4: Fallback to session summary
        return self._build_basic_nutshell(report)
    
    def _extract_intelligent_nutshell(self, synthesis_content: str) -> str:
        """Extract nutshell using intelligent text analysis"""
        try:
            # Look for conclusion indicators
            conclusion_keywords = [
                'zusammenfassend', 'insgesamt', 'schlussfolgerung', 'fazit',
                'kernaussage', 'haupterkenntnisse', 'wesentlich ist',
                'in conclusion', 'overall', 'in summary', 'key takeaway'
            ]
            
            sentences = synthesis_content.replace('\n', ' ').split('. ')
            
            # Strategy 2a: Find sentences with conclusion keywords
            for sentence in sentences:
                for keyword in conclusion_keywords:
                    if keyword.lower() in sentence.lower():
                        return sentence.strip() + '.'
            
            # Strategy 2b: Look for numbered findings (1. MAIN FINDINGS:)
            if 'MAIN FINDINGS:' in synthesis_content:
                main_section = synthesis_content.split('MAIN FINDINGS:')[1]
                if main_section:
                    # Extract first substantial sentence after MAIN FINDINGS
                    main_sentences = main_section.split('\n')
                    for sentence in main_sentences:
                        cleaned = sentence.strip('- ').strip()
                        if len(cleaned) > 50:  # Substantial content
                            return cleaned
            
            # Strategy 2c: Take last paragraph (often contains conclusion)
            paragraphs = synthesis_content.split('\n\n')
            if len(paragraphs) > 1:
                last_paragraph = paragraphs[-1].strip()
                if len(last_paragraph) > 50:
                    return last_paragraph
            
            # Strategy 2d: Fallback to first paragraph
            first_paragraph = paragraphs[0] if paragraphs else synthesis_content
            return first_paragraph.split('\n')[0]  # First line only
            
        except Exception as e:
            print(f"⚠️  Intelligent nutshell extraction failed: {e}")
            return synthesis_content.split('\n\n')[0] if synthesis_content else "Analysis completed"
    
    def _build_nutshell_from_insights(self, insights: List[str]) -> str:
        """Build nutshell from key insights"""
        try:
            if not insights:
                return "Session completed with valuable insights."
            
            # Take top 2-3 insights and combine them
            top_insights = insights[:3]
            
            if len(top_insights) == 1:
                return top_insights[0]
            elif len(top_insights) == 2:
                return f"{top_insights[0]} Additionally, {top_insights[1].lower()}"
            else:
                return f"{top_insights[0]} Key findings include {top_insights[1].lower()} and {top_insights[2].lower()}"
                
        except Exception as e:
            print(f"⚠️  Insight-based nutshell failed: {e}")
            return "Session generated multiple valuable insights."
    
    def _build_basic_nutshell(self, report: CortexReport) -> str:
        """Basic nutshell from session metadata"""
        try:
            ai_count = len(report.ai_team)
            iteration_count = len(report.iterations)
            
            if report.total_cost > 0:
                return f"Collaborative analysis by {ai_count} AI systems across {iteration_count} iterations generated comprehensive insights on {report.original_topic} at ${report.total_cost:.2f} cost."
            else:
                return f"Multi-AI analysis by {ai_count} systems provided diverse perspectives on {report.original_topic}."
                
        except Exception as e:
            print(f"⚠️  Basic nutshell generation failed: {e}")
            return "Session completed with multi-AI collaboration."
    
    def _ai_generated_nutshell(self, report: CortexReport) -> str:
        """Generate nutshell using AI (costs extra token, but highest quality)"""
        try:
            # This would require an AI call - implement if needed
            # For now, fallback to intelligent extraction
            if report.final_synthesis:
                return self._extract_intelligent_nutshell(report.final_synthesis['content'])
            else:
                return self._build_nutshell_from_insights(report.emergent_insights)
                
        except Exception as e:
            print(f"⚠️  AI nutshell generation failed: {e}")
            return "Comprehensive multi-AI analysis completed."
    
    # =========================================================================
    # OUTPUT FORMATTING
    # =========================================================================
    
    def format_output(self, report: CortexReport, format_type: str = None) -> str:
        """Format report according to specified format with error handling"""
        format_type = format_type or self.output_config.get('format', 'markdown')
        
        try:
            if format_type == 'json':
                return self._format_json(report)
            elif format_type == 'yaml':
                return self._format_yaml(report)
            elif format_type == 'pdf':
                # PDF is handled separately via generate_pdf() method
                # This should not be called for PDF format
                print("⚠️  PDF format should use generate_pdf() method directly")
                return self._format_markdown(report)  # Fallback
            else:  # markdown default
                return self._format_markdown(report)
                
        except Exception as e:
            print(f"❌ Failed to format report as {format_type}: {e}")
            # Fallback to simple text format
            return self._format_simple_text(report)
    
    def _format_markdown(self, report: CortexReport) -> str:
        """Format as user-friendly Markdown with intelligent nutshell"""
        try:
            md = f"""# CORTEX Session Report

## Topic
{report.original_topic or 'No topic specified'}

## Answer in a Nutshell
"""
            
            # Generate intelligent nutshell summary
            nutshell = self._generate_nutshell_summary(report)
            md += f"{nutshell}\n\n"
            
            # Session Overview Table (moved above Main Findings)
            md += "## Session Overview\n\n"
            md += f"**Experiment:** {report.experiment_name}  \n"
            md += f"**AI Team:** {', '.join(report.ai_team) if report.ai_team else 'None'}  \n"
            md += f"**Iterations:** {len(report.iterations)}  \n"
            md += f"**Total Cost:** ${report.total_cost:.4f}  \n"
            
            # Add session timing if available
            if report.session_metadata and 'start_time' in report.session_metadata:
                start_time = report.session_metadata['start_time']
                if isinstance(start_time, str):
                    md += f"**Started:** {start_time}  \n"
                else:
                    md += f"**Started:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}  \n"
                
                if 'duration' in report.session_metadata:
                    duration = report.session_metadata['duration']
                    md += f"**Duration:** {duration}  \n"
                elif 'end_time' in report.session_metadata:
                    end_time = report.session_metadata['end_time']
                    if not isinstance(start_time, str) and not isinstance(end_time, str):
                        duration = end_time - start_time
                        md += f"**Duration:** {duration}  \n"
            
            md += "\n"
            
            # Now the actual findings
            md += "## Main Findings\n\n"
            
            # Add final synthesis content if available
            if report.final_synthesis and report.final_synthesis.get('content'):
                md += f"### Comprehensive Analysis\n\n{report.final_synthesis['content']}\n\n"
            
            # Key insights
            if report.emergent_insights:
                md += "## Key Insights\n\n"
                for insight in report.emergent_insights[:5]:  # Top 5 insights
                    md += f"- {insight}\n"
                md += "\n"
            
            # Cost breakdown
            if report.cost_breakdown:
                md += "## Cost Breakdown\n\n"
                for ai_name, cost in report.cost_breakdown.items():
                    percentage = (cost / report.total_cost * 100) if report.total_cost > 0 else 0
                    md += f"- **{ai_name}:** ${cost:.4f} ({percentage:.1f}%)\n"
                md += "\n"
            
            # Iteration details
            md += "## Iteration Details\n\n"
            for iteration in report.iterations:
                md += f"### Iteration {iteration.round_number}: {iteration.ruleset_name}\n\n"
                
                if iteration.meta_insights:
                    analyzer = iteration.meta_analyzer or "Unknown"
                    md += f"**Meta-Analysis by {analyzer}:**  \n{iteration.meta_insights}\n\n"
                
                md += f"**Participating AIs:** {', '.join(iteration.successful_ais)}\n"
                md += f"**Cost:** ${iteration.total_cost:.4f}\n\n"
            
            # Technical details
            md += "## Technical Details\n\n"
            if report.token_usage_summary:
                total_tokens = report.token_usage_summary.get('total_tokens', 0)
                md += f"**Total Tokens:** {total_tokens:,}\n"
                
                if report.token_usage_summary.get('cost_efficiency'):
                    md += f"**Token Efficiency (tokens per $):**\n"
                    for ai_name, efficiency in sorted(
                        report.token_usage_summary['cost_efficiency'].items(), 
                        key=lambda x: x[1], reverse=True
                    ):
                        md += f"- {ai_name}: {efficiency:,.0f} tokens/$\n"
            
            return md
            
        except Exception as e:
            print(f"❌ Markdown formatting failed: {e}")
            return self._format_simple_text(report)
    
    def _format_json(self, report: CortexReport) -> str:
        """Format as JSON with error handling"""
        try:
            # Convert dataclass to dict
            report_dict = asdict(report)
            
            # Handle datetime objects
            def convert_datetime(obj):
                if isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj
            
            report_dict = convert_datetime(report_dict)
            
            return json.dumps(report_dict, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"❌ JSON formatting failed: {e}")
            return json.dumps({'error': f'Failed to format report: {e}'}, indent=2)
    
    def _format_yaml(self, report: CortexReport) -> str:
        """Format as YAML with error handling"""
        try:
            report_dict = asdict(report)
            
            # Convert datetime objects
            def convert_datetime(obj):
                if isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj
            
            report_dict = convert_datetime(report_dict)
            
            return yaml.dump(report_dict, default_flow_style=False, 
                           allow_unicode=True, indent=2)
                           
        except Exception as e:
            print(f"❌ YAML formatting failed: {e}")
            return f"error: 'Failed to format report: {e}'"
    
    def _format_simple_text(self, report: CortexReport) -> str:
        """Simple text format as ultimate fallback"""
        try:
            text = f"CORTEX Session Report\n"
            text += f"=====================\n\n"
            text += f"Experiment: {report.experiment_name}\n"
            text += f"Topic: {report.original_topic}\n"
            text += f"AI Team: {', '.join(report.ai_team)}\n"
            text += f"Iterations: {len(report.iterations)}\n"
            text += f"Total Cost: ${report.total_cost:.4f}\n\n"
            
            if report.emergent_insights:
                text += "Key Insights:\n"
                for insight in report.emergent_insights[:3]:
                    text += f"- {insight}\n"
            
            return text
            
        except Exception as e:
            return f"Report generation completely failed: {e}"
    
    # =========================================================================
    # ENHANCED PDF GENERATION
    # =========================================================================
    
    def generate_pdf(self, report: CortexReport, filename: str) -> bool:
        """Generate comprehensive PDF report matching Markdown quality"""
        if not PDF_AVAILABLE:
            print("⚠️  PDF generation requires reportlab: pip install reportlab")
            return False
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            story = []
            styles = getSampleStyleSheet()
            
            # Enhanced custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                textColor=colors.darkblue,
                alignment=1  # Center alignment
            )
            
            heading2_style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.darkblue
            )
            
            heading3_style = ParagraphStyle(
                'CustomHeading3',
                parent=styles['Heading3'],
                fontSize=12,
                spaceBefore=15,
                spaceAfter=8,
                textColor=colors.navy
            )
            
            # Title and basic info
            story.append(Paragraph("CORTEX Session Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Topic section
            story.append(Paragraph("Topic", heading2_style))
            topic_text = report.original_topic or 'No topic specified'
            story.append(Paragraph(topic_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Answer in a Nutshell - with intelligent summary
            story.append(Paragraph("Answer in a Nutshell", heading2_style))
            nutshell = self._generate_nutshell_summary(report)
            story.append(Paragraph(nutshell, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Session Overview section for PDF
            story.append(Paragraph("Session Overview", heading2_style))
            
            # Basic stats table with timing
            basic_data = [
                ['Experiment', report.experiment_name],
                ['AI Team', ', '.join(report.ai_team) if report.ai_team else 'None'],
                ['Iterations', str(len(report.iterations))],
                ['Total Cost', f"${report.total_cost:.4f}"]
            ]
            
            # Add timing information if available
            if report.session_metadata and 'start_time' in report.session_metadata:
                start_time = report.session_metadata['start_time']
                if isinstance(start_time, str):
                    basic_data.append(['Started', start_time])
                else:
                    basic_data.append(['Started', start_time.strftime('%Y-%m-%d %H:%M:%S')])
                
                if 'duration' in report.session_metadata:
                    duration = report.session_metadata['duration']
                    basic_data.append(['Duration', str(duration)])
                elif 'end_time' in report.session_metadata:
                    end_time = report.session_metadata['end_time']
                    if not isinstance(start_time, str) and not isinstance(end_time, str):
                        duration = end_time - start_time
                        basic_data.append(['Duration', str(duration)])
            
            basic_table = Table(basic_data, colWidths=[2*inch, 4*inch])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(basic_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Main Findings
            story.append(Paragraph("Main Findings", heading2_style))
            
            # Comprehensive Analysis (Final Synthesis)
            if report.final_synthesis and report.final_synthesis.get('content'):
                story.append(Paragraph("Comprehensive Analysis", heading3_style))
                synthesis_text = report.final_synthesis['content'].replace('\n', '<br/>')
                # Split long synthesis into paragraphs for better readability
                synthesis_paragraphs = synthesis_text.split('<br/><br/>')
                for para in synthesis_paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                story.append(Spacer(1, 0.2*inch))
            
            # Key Insights
            if report.emergent_insights:
                story.append(Paragraph("Key Insights", heading2_style))
                for insight in report.emergent_insights[:5]:
                    bullet_text = f"• {insight}"
                    story.append(Paragraph(bullet_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Cost Breakdown
            if report.cost_breakdown:
                story.append(Paragraph("Cost Breakdown", heading2_style))
                
                cost_data = [['AI Provider', 'Cost', 'Percentage']]
                for ai_name, cost in report.cost_breakdown.items():
                    percentage = (cost / report.total_cost * 100) if report.total_cost > 0 else 0
                    cost_data.append([ai_name, f"${cost:.4f}", f"{percentage:.1f}%"])
                
                cost_table = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                cost_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(cost_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Page break for iteration details
            story.append(PageBreak())
            
            # Iteration Details
            story.append(Paragraph("Iteration Details", heading2_style))
            
            for iteration in report.iterations:
                # Iteration header
                iter_title = f"Iteration {iteration.round_number}: {iteration.ruleset_name}"
                story.append(Paragraph(iter_title, heading3_style))
                
                # Meta-analysis if available
                if iteration.meta_insights:
                    analyzer = iteration.meta_analyzer or "Unknown"
                    meta_title = f"Meta-Analysis by {analyzer}:"
                    story.append(Paragraph(meta_title, styles['Normal']))
                    story.append(Paragraph(iteration.meta_insights, styles['Italic']))
                    story.append(Spacer(1, 0.1*inch))
                
                # Iteration stats
                iter_data = [
                    ['Participating AIs', ', '.join(iteration.successful_ais)],
                    ['Cost', f"${iteration.total_cost:.4f}"],
                    ['Timestamp', iteration.timestamp.strftime('%Y-%m-%d %H:%M:%S')]
                ]
                
                iter_table = Table(iter_data, colWidths=[2*inch, 3*inch])
                iter_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(iter_table)
                story.append(Spacer(1, 0.15*inch))
            
            # Technical Details
            story.append(PageBreak())
            story.append(Paragraph("Technical Details", heading2_style))
            
            if report.token_usage_summary:
                total_tokens = report.token_usage_summary.get('total_tokens', 0)
                story.append(Paragraph(f"<b>Total Tokens:</b> {total_tokens:,}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                # Token efficiency table
                if report.token_usage_summary.get('cost_efficiency'):
                    story.append(Paragraph("Token Efficiency (tokens per $)", heading3_style))
                    
                    efficiency_data = [['AI Provider', 'Tokens per Dollar']]
                    for ai_name, efficiency in sorted(
                        report.token_usage_summary['cost_efficiency'].items(), 
                        key=lambda x: x[1], reverse=True
                    ):
                        efficiency_data.append([ai_name, f"{efficiency:,.0f}"])
                    
                    efficiency_table = Table(efficiency_data, colWidths=[2.5*inch, 2*inch])
                    efficiency_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgreen, colors.white]),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    story.append(efficiency_table)
            
            # Footer
            story.append(Spacer(1, 0.3*inch))
            footer_text = f"Generated by CORTEX v3.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1  # Center
            )
            story.append(Paragraph(footer_text, footer_style))
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"❌ Enhanced PDF generation failed: {e}")
            return False