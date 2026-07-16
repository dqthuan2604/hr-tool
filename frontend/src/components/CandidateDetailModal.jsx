import { useState, useEffect, useRef } from 'react';
import { getCandidateVersions, saveCandidateVersion, restoreCandidateVersion } from '../api/candidates';
import { X, User, Envelope, Phone, LinkedinLogo, Briefcase, Plus, GraduationCap, Code, Folder } from '@phosphor-icons/react';
import { useToast } from './Toast';
import ConfirmModal from './ConfirmModal';

export default function CandidateDetailModal({ candidate, onClose, onUpdate }) {
  const [profile, setProfile] = useState({});
  const [versions, setVersions] = useState([]);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('edit'); // 'edit', 'versions'
  const [activeSection, setActiveSection] = useState('basic_info');
  const [confirmRestore, setConfirmRestore] = useState(null);
  const overlayRef = useRef(null);
  const toast = useToast();

  useEffect(() => {
    if (candidate) {
      const currentVersion = candidate.versions?.find(v => v.is_current) || candidate.versions?.[0];
      setProfile(currentVersion?.profile_json || {});
      loadVersions();
    }
  }, [candidate]);

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose();
  };

  const loadVersions = async () => {
    try {
      const data = await getCandidateVersions(candidate.id);
      setVersions(data);
    } catch (err) {
      toast.error('Lỗi khi tải lịch sử phiên bản');
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await saveCandidateVersion(candidate.id, profile);
      await loadVersions();
      onUpdate();
      toast.success('Đã lưu thành công phiên bản mới!');
    } catch (err) {
      toast.error('Lỗi khi lưu');
    } finally {
      setIsSaving(false);
    }
  };

  const handleRestore = async (versionId) => {
    setConfirmRestore(versionId);
  };
  
  const executeRestore = async () => {
    if (!confirmRestore) return;
    try {
      await restoreCandidateVersion(candidate.id, confirmRestore);
      await loadVersions();
      onUpdate();
      const currentVersion = versions.find(v => v.id === confirmRestore);
      if (currentVersion) setProfile(currentVersion.profile_json);
      toast.success('Đã khôi phục thành công!');
    } catch (err) {
      toast.error('Lỗi khi khôi phục');
    } finally {
      setConfirmRestore(null);
    }
  };

  const updateBasicInfo = (key, value) => {
    setProfile(prev => ({
      ...prev,
      basic_info: { ...(prev.basic_info || {}), [key]: value }
    }));
  };

  if (!candidate) return null;

  const basicInfo = profile.basic_info || {};
  const workExp = profile.work_experiences || [];
  const educations = profile.educations || [];
  const projects = profile.projects || [];
  const skills = profile.skills || [];

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)' }}
    >
      <div
        className="w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden rounded-2xl shadow-2xl animate-fade-up"
        style={{
          background: 'var(--bg-overlay)',
          border: '1px solid var(--border)',
        }}
      >
        
        {/* Header */}
        <div
          className="flex justify-between items-center p-5"
          style={{ borderBottom: '1px solid var(--border-subtle)' }}
        >
          <div>
            <h2 className="text-lg font-bold leading-tight" style={{ color: 'var(--text-primary)' }}>
              Chi tiết Hồ sơ
            </h2>
            <p className="text-[11px] mt-1 font-mono" style={{ color: 'var(--text-muted)' }}>
              {candidate.source_file}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Tabs */}
            <div
              className="flex p-1 rounded-lg"
              style={{ background: 'var(--bg-raised)', border: '1px solid var(--border-subtle)' }}
            >
              <button
                onClick={() => setActiveTab('edit')}
                className="px-4 py-1.5 text-xs font-medium rounded-md transition-all"
                style={{
                  background: activeTab === 'edit' ? 'var(--accent-muted)' : 'transparent',
                  color: activeTab === 'edit' ? 'var(--accent-hover)' : 'var(--text-muted)',
                }}
              >
                Chỉnh sửa
              </button>
              <button
                onClick={() => setActiveTab('versions')}
                className="px-4 py-1.5 text-xs font-medium rounded-md transition-all"
                style={{
                  background: activeTab === 'versions' ? 'var(--accent-muted)' : 'transparent',
                  color: activeTab === 'versions' ? 'var(--accent-hover)' : 'var(--text-muted)',
                }}
              >
                Lịch sử ({versions.length})
              </button>
            </div>
            
            {/* Close */}
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 transition-all"
              style={{ color: 'var(--text-muted)' }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'var(--bg-raised)';
                e.currentTarget.style.color = 'var(--text-primary)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = 'var(--text-muted)';
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Body */}
        <div
          className="flex-grow overflow-y-auto p-6"
          style={{ background: 'var(--bg-base)' }}
        >
          {activeTab === 'edit' ? (
            <div className="flex flex-col md:flex-row h-full -m-6 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
              {/* Sidebar */}
              <div className="w-full md:w-64 flex-shrink-0 p-4 md:p-6 space-y-1 overflow-y-auto border-r" style={{ borderColor: 'var(--border-subtle)', background: 'var(--bg-surface)' }}>
                {[
                  { id: 'basic_info', label: 'Thông tin cơ bản', icon: <User size={16} /> },
                  { id: 'work_experiences', label: 'Kinh nghiệm', icon: <Briefcase size={16} /> },
                  { id: 'educations', label: 'Học vấn', icon: <GraduationCap size={16} /> },
                  { id: 'projects', label: 'Dự án', icon: <Folder size={16} /> },
                  { id: 'skills', label: 'Kỹ năng', icon: <Code size={16} /> },
                ].map(sec => (
                  <button
                    key={sec.id}
                    onClick={() => setActiveSection(sec.id)}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left"
                    style={{
                      background: activeSection === sec.id ? 'var(--accent-muted)' : 'transparent',
                      color: activeSection === sec.id ? 'var(--text-primary)' : 'var(--text-muted)'
                    }}
                  >
                    {sec.icon}
                    {sec.label}
                  </button>
                ))}
              </div>
              
              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6 md:p-8" style={{ background: 'var(--bg-base)' }}>
                <div className="max-w-3xl mx-auto space-y-6">
                  {activeSection === 'basic_info' && (
                    <>
{/* Basic Info */}
              <div
                className="transition-colors"
                
              >
                <div className="flex items-center gap-2 mb-5 pb-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <User size={16} style={{ color: 'var(--accent-hover)' }} />
                  <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Thông tin cơ bản</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-5">
                  <div>
                    <label className="block text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-muted)' }}>
                      Họ tên
                    </label>
                    <input
                      type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                      value={basicInfo.full_name || ''}
                      onChange={e => updateBasicInfo('full_name', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-muted)' }}>
                      Email
                    </label>
                    <div className="relative">
                      <Envelope size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                      <input
                        type="email" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors pl-9 pr-3 py-2"
                        value={basicInfo.email || ''}
                        onChange={e => updateBasicInfo('email', e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-muted)' }}>
                      Số điện thoại
                    </label>
                    <div className="relative">
                      <Phone size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                      <input
                        type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors pl-9 pr-3 py-2"
                        value={basicInfo.phone || ''}
                        onChange={e => updateBasicInfo('phone', e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-muted)' }}>
                      LinkedIn
                    </label>
                    <div className="relative">
                      <LinkedinLogo size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
                      <input
                        type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors pl-9 pr-3 py-2"
                        value={basicInfo.linkedin || ''}
                        onChange={e => updateBasicInfo('linkedin', e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="col-span-2">
                    <label className="block text-[10px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-muted)' }}>
                      Summary
                    </label>
                    <textarea
                          className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2 min-h-[100px]"
                          value={basicInfo.summary || ''}
                          onChange={e => updateBasicInfo('summary', e.target.value)}
                    />
                  </div>
                </div>
              </div>
                  </>)}
                  {activeSection === 'work_experiences' && (
                    <>
{/* Work Exp */}
              <div
                className="transition-colors"
                
              >
                <div className="flex justify-between items-center mb-5 pb-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="flex items-center gap-2">
                    <Briefcase size={16} style={{ color: 'var(--accent-hover)' }} />
                    <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Kinh nghiệm làm việc</h3>
                  </div>
                  <button
                    onClick={() => setProfile(p => ({...p, work_experiences: [...(p.work_experiences || []), {company:'', role:'', start_date:'', end_date:'', description:''}]}))}
                    className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg transition-colors"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                  >
                    <Plus size={12} weight="bold" />
                    Thêm mục
                  </button>
                </div>
                
                <div className="space-y-4">
                  {workExp.length === 0 ? (
                    <p className="text-xs text-center py-4" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu kinh nghiệm làm việc.</p>
                  ) : workExp.map((exp, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-lg relative group"
                      style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}
                    >
                      <button
                        className="absolute top-2 right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: '#f87171', background: 'rgba(239,68,68,0.1)' }}
                        onClick={() => {
                          const newExp = [...workExp];
                          newExp.splice(i, 1);
                          setProfile({...profile, work_experiences: newExp});
                        }}
                      >
                        <X size={12} />
                      </button>
                      <div className="grid grid-cols-2 gap-4 mb-4 pr-6">
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Công ty</label>
                          <input
                            className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={exp.company || ''}
                            onChange={e => {
                              const newExp = [...workExp]; newExp[i].company = e.target.value; setProfile({...profile, work_experiences: newExp});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Vị trí</label>
                          <input
                            className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={exp.role || ''}
                            onChange={e => {
                              const newExp = [...workExp]; newExp[i].role = e.target.value; setProfile({...profile, work_experiences: newExp});
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Mô tả công việc</label>
                        <textarea
                          className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2 min-h-[100px]"
                          value={exp.description || ''}
                          onChange={e => {
                            const newExp = [...workExp]; newExp[i].description = e.target.value; setProfile({...profile, work_experiences: newExp});
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
                  </>)}
                  {activeSection === 'educations' && (
                    <>
{/* Educations */}
              <div
                className="transition-colors"
                
              >
                <div className="flex justify-between items-center mb-5 pb-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="flex items-center gap-2">
                    <GraduationCap size={16} style={{ color: 'var(--accent-hover)' }} />
                    <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Học vấn</h3>
                  </div>
                  <button
                    onClick={() => setProfile(p => ({...p, educations: [...(p.educations || []), {school:'', degree:'', major:'', gpa:'', start_date:'', end_date:'', description:''}]}))}
                    className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg transition-colors"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                  >
                    <Plus size={12} weight="bold" />
                    Thêm mục
                  </button>
                </div>
                
                <div className="space-y-4">
                  {educations.length === 0 ? (
                    <p className="text-xs text-center py-4" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu học vấn.</p>
                  ) : educations.map((edu, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-lg relative group"
                      style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}
                    >
                      <button
                        className="absolute top-2 right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: '#f87171', background: 'rgba(239,68,68,0.1)' }}
                        onClick={() => {
                          const newEdu = [...educations];
                          newEdu.splice(i, 1);
                          setProfile({...profile, educations: newEdu});
                        }}
                      >
                        <X size={12} />
                      </button>
                      <div className="grid grid-cols-2 gap-4 mb-4 pr-6">
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Trường</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={edu.school || ''}
                            onChange={e => {
                              const newEdu = [...educations];
                              newEdu[i].school = e.target.value;
                              setProfile({...profile, educations: newEdu});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Chuyên ngành</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={edu.major || ''}
                            onChange={e => {
                              const newEdu = [...educations];
                              newEdu[i].major = e.target.value;
                              setProfile({...profile, educations: newEdu});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Thời gian bắt đầu</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={edu.start_date || ''}
                            onChange={e => {
                              const newEdu = [...educations];
                              newEdu[i].start_date = e.target.value;
                              setProfile({...profile, educations: newEdu});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Thời gian kết thúc</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={edu.end_date || ''}
                            onChange={e => {
                              const newEdu = [...educations];
                              newEdu[i].end_date = e.target.value;
                              setProfile({...profile, educations: newEdu});
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Mô tả</label>
                        <textarea
                          className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2 min-h-[100px]"
                          value={edu.description || ''}
                          onChange={e => {
                            const newEdu = [...educations];
                            newEdu[i].description = e.target.value;
                            setProfile({...profile, educations: newEdu});
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
                  </>)}
                  {activeSection === 'projects' && (
                    <>
{/* Projects */}
              <div
                className="transition-colors"
                
              >
                <div className="flex justify-between items-center mb-5 pb-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="flex items-center gap-2">
                    <Folder size={16} style={{ color: 'var(--accent-hover)' }} />
                    <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Dự án</h3>
                  </div>
                  <button
                    onClick={() => setProfile(p => ({...p, projects: [...(p.projects || []), {name:'', url:'', start_date:'', end_date:'', description:''}]}))}
                    className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg transition-colors"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                  >
                    <Plus size={12} weight="bold" />
                    Thêm mục
                  </button>
                </div>
                
                <div className="space-y-4">
                  {projects.length === 0 ? (
                    <p className="text-xs text-center py-4" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu dự án.</p>
                  ) : projects.map((proj, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-lg relative group"
                      style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}
                    >
                      <button
                        className="absolute top-2 right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: '#f87171', background: 'rgba(239,68,68,0.1)' }}
                        onClick={() => {
                          const newProj = [...projects];
                          newProj.splice(i, 1);
                          setProfile({...profile, projects: newProj});
                        }}
                      >
                        <X size={12} />
                      </button>
                      <div className="grid grid-cols-2 gap-4 mb-4 pr-6">
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Tên dự án</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={proj.name || ''}
                            onChange={e => {
                              const newProj = [...projects];
                              newProj[i].name = e.target.value;
                              setProfile({...profile, projects: newProj});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>URL</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={proj.url || ''}
                            onChange={e => {
                              const newProj = [...projects];
                              newProj[i].url = e.target.value;
                              setProfile({...profile, projects: newProj});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Thời gian bắt đầu</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={proj.start_date || ''}
                            onChange={e => {
                              const newProj = [...projects];
                              newProj[i].start_date = e.target.value;
                              setProfile({...profile, projects: newProj});
                            }}
                          />
                        </div>
                        <div>
                          <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Thời gian kết thúc</label>
                          <input
                            type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                            value={proj.end_date || ''}
                            onChange={e => {
                              const newProj = [...projects];
                              newProj[i].end_date = e.target.value;
                              setProfile({...profile, projects: newProj});
                            }}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Mô tả</label>
                        <textarea
                          className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2 min-h-[100px]"
                          value={proj.description || ''}
                          onChange={e => {
                            const newProj = [...projects];
                            newProj[i].description = e.target.value;
                            setProfile({...profile, projects: newProj});
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
                  </>)}
                  {activeSection === 'skills' && (
                    <>
{/* Skills */}
              <div
                className="transition-colors"
                
              >
                <div className="flex justify-between items-center mb-5 pb-3" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <div className="flex items-center gap-2">
                    <Code size={16} style={{ color: 'var(--accent-hover)' }} />
                    <h3 className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>Kỹ năng</h3>
                  </div>
                  <button
                    onClick={() => setProfile(p => ({...p, skills: [...(p.skills || []), {category:'Khác', items:[]}]}))}
                    className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg transition-colors"
                    style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                  >
                    <Plus size={12} weight="bold" />
                    Thêm mục
                  </button>
                </div>
                
                <div className="space-y-4">
                  {skills.length === 0 ? (
                    <p className="text-xs text-center py-4" style={{ color: 'var(--text-disabled)' }}>Không có dữ liệu kỹ năng.</p>
                  ) : skills.map((skill, i) => (
                    <div
                      key={i}
                      className="p-4 rounded-lg relative group"
                      style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}
                    >
                      <button
                        className="absolute top-2 right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ color: '#f87171', background: 'rgba(239,68,68,0.1)' }}
                        onClick={() => {
                          const newSkills = [...skills];
                          newSkills.splice(i, 1);
                          setProfile({...profile, skills: newSkills});
                        }}
                      >
                        <X size={12} />
                      </button>
                      <div className="mb-3 pr-6">
                        <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Nhóm kỹ năng</label>
                        <input
                          type="text" className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2"
                          value={skill.category || ''}
                          onChange={e => {
                            const newSkills = [...skills];
                            newSkills[i].category = e.target.value;
                            setProfile({...profile, skills: newSkills});
                          }}
                        />
                      </div>
                      <div>
                        <label className="block text-[9px] uppercase tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Các kỹ năng (mỗi dòng 1 mục)</label>
                        <textarea
                          className="w-full bg-neutral-800/20 text-sm rounded-lg border border-neutral-700/40 focus:border-indigo-500/50 outline-none transition-colors px-3 py-2 min-h-[100px]"
                          value={(skill.items || []).join('\n')}
                          onChange={e => {
                            const newSkills = [...skills];
                            newSkills[i].items = e.target.value.split('\n');
                            setProfile({...profile, skills: newSkills});
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
                  </>)}
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              <div
                className="rounded-xl overflow-hidden"
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
              >
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)' }}>
                      <th className="px-5 py-3 text-[10px] font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Version</th>
                      <th className="px-5 py-3 text-[10px] font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Ngày lưu</th>
                      <th className="px-5 py-3 text-[10px] font-semibold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Trạng thái</th>
                      <th className="px-5 py-3 text-[10px] font-semibold uppercase tracking-widest text-right" style={{ color: 'var(--text-muted)' }}>Hành động</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.map((v, i) => (
                      <tr key={v.id} style={{ borderBottom: i !== versions.length - 1 ? '1px solid var(--border-subtle)' : 'none' }}>
                        <td className="px-5 py-4 text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                          v{v.version_number}
                        </td>
                        <td className="px-5 py-4 text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
                          {new Date(v.created_at).toLocaleString('vi-VN')}
                        </td>
                        <td className="px-5 py-4">
                          {v.is_current ? (
                            <span className="badge-success text-[10px] px-2 py-0.5 rounded-full font-medium">Hiện tại</span>
                          ) : (
                            <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: 'var(--bg-raised)', color: 'var(--text-muted)' }}>Lịch sử</span>
                          )}
                        </td>
                        <td className="px-5 py-4 text-right">
                          {!v.is_current && (
                            <button
                              onClick={() => handleRestore(v.id)}
                              className="text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
                              style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)' }}
                            >
                              Khôi phục
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {activeTab === 'edit' && (
          <div
            className="p-5 flex justify-end gap-3"
            style={{ borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-overlay)' }}
          >
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-xl text-sm font-semibold transition-all"
              style={{ color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)' }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-raised)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              Hủy
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-semibold transition-all"
              style={{
                background: isSaving ? 'var(--bg-raised)' : 'var(--accent)',
                color: isSaving ? 'var(--text-disabled)' : '#fff',
                cursor: isSaving ? 'not-allowed' : 'pointer'
              }}
            >
              {isSaving ? (
                <>
                  <span className="w-3.5 h-3.5 rounded-full border-2" style={{ borderColor: 'var(--border)', borderTopColor: 'var(--text-secondary)', animation: 'spin 0.8s linear infinite' }} />
                  Đang lưu...
                </>
              ) : 'Lưu thành Version mới'}
            </button>
          </div>
        )}
      </div>

      {confirmRestore && (
        <ConfirmModal 
          title="Khôi phục phiên bản" 
          message="Khôi phục phiên bản này? (Hệ thống sẽ tạo ra 1 phiên bản mới sao chép nội dung của phiên bản này)"
          onConfirm={executeRestore}
          onCancel={() => setConfirmRestore(null)}
          confirmText="Khôi phục"
          variant="primary"
        />
      )}
    </div>
  );
}
